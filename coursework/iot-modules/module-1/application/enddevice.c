#include "OSAL.h"
#include "AF.h"
#include "ZDApp.h"
#include "ZDObject.h"
#include "ZDProfile.h"
#include "GenericApp.h"
#include "DebugTrace.h"
#include <stdio.h> // 【新增】用于 sprintf 格式化数据帧

#if !defined( WIN32 )
  #include "OnBoard.h"
#endif

/* HAL */
#include "hal_lcd.h"
#include "hal_led.h"
#include "hal_key.h"
#include "hal_uart.h"

#include "DHT11.h"
#include "ds18b20.h"

const cId_t GenericApp_ClusterList[GENERICAPP_MAX_CLUSTERS] =
{
  GENERICAPP_CLUSTERID,
  GenericApp_Sensor_CLUSTERID
};

const SimpleDescriptionFormat_t GenericApp_SimpleDesc =
{
  GENERICAPP_ENDPOINT,              //  int Endpoint;
  GENERICAPP_PROFID,                //  uint16 AppProfId[2];
  GENERICAPP_DEVICEID,              //  uint16 AppDeviceId[2];
  GENERICAPP_DEVICE_VERSION,        //  int   AppDevVer:4;
  GENERICAPP_FLAGS,                 //  int   AppFlags:4;
  GENERICAPP_MAX_CLUSTERS,          //  byte  AppNumInClusters;
  (cId_t *)GenericApp_ClusterList,  //  byte *pAppInClusterList;
  GENERICAPP_MAX_CLUSTERS,          //  byte  AppNumInClusters;
  (cId_t *)GenericApp_ClusterList   //  byte *pAppInClusterList;
};

endPointDesc_t GenericApp_epDesc;
byte GenericApp_TaskID; 
devStates_t GenericApp_NwkState;
byte GenericApp_TransID; 
afAddrType_t GenericApp_DstAddr;

char bianhaoID = '2'; // 节点编号

static void GenericApp_ProcessZDOMsgs( zdoIncomingMsg_t *inMsg );
static void GenericApp_HandleKeys( byte shift, byte keys );
static void GenericApp_MessageMSGCB( afIncomingMSGPacket_t *pckt );
void GenericApp_Send_Sensor_Message( void );
uint16 myApp_ReadLightLevel( void );
uint16 myApp_ReadGasLevel( void );

void GenericApp_Init( uint8 task_id )
{
  GenericApp_TaskID = task_id;
  GenericApp_NwkState = DEV_INIT;
  GenericApp_TransID = 0;
  
  // 初始化 PIR 输入
  P0_5 = 0;

  // 配置 P1_3 为输出，用于驱动继电器
  P1SEL &= ~0x08; 
  P1DIR |= 0x08;  
  P1_3 = 0;       // 初始化继电器为关闭

  // 配置目标地址为协调器
  GenericApp_DstAddr.addrMode = (afAddrMode_t)Addr16Bit;
  GenericApp_DstAddr.endPoint = GENERICAPP_ENDPOINT;
  GenericApp_DstAddr.addr.shortAddr = 0x0000;

  GenericApp_epDesc.endPoint = GENERICAPP_ENDPOINT;
  GenericApp_epDesc.task_id = &GenericApp_TaskID;
  GenericApp_epDesc.simpleDesc = (SimpleDescriptionFormat_t *)&GenericApp_SimpleDesc;
  GenericApp_epDesc.latencyReq = noLatencyReqs;

  afRegister( &GenericApp_epDesc );
  RegisterForKeys( GenericApp_TaskID );

  ZDO_RegisterForZDOMsg( GenericApp_TaskID, End_Device_Bind_rsp );
  ZDO_RegisterForZDOMsg( GenericApp_TaskID, Match_Desc_rsp );
}

uint16 GenericApp_ProcessEvent( uint8 task_id, uint16 events )
{
  afIncomingMSGPacket_t *MSGpkt;
  
  if ( events & SYS_EVENT_MSG )
  {
    MSGpkt = (afIncomingMSGPacket_t *)osal_msg_receive( GenericApp_TaskID );
    while ( MSGpkt )
    {
      switch ( MSGpkt->hdr.event )
      {
        case ZDO_CB_MSG:
          GenericApp_ProcessZDOMsgs( (zdoIncomingMsg_t *)MSGpkt );
          break;
        case KEY_CHANGE:
          GenericApp_HandleKeys( ((keyChange_t *)MSGpkt)->state, ((keyChange_t *)MSGpkt)->keys );
          break;
        case AF_INCOMING_MSG_CMD:
          GenericApp_MessageMSGCB( MSGpkt );
          break;
        case ZDO_STATE_CHANGE:
          GenericApp_NwkState = (devStates_t)(MSGpkt->hdr.status);
          if ( GenericApp_NwkState == DEV_END_DEVICE )
          {
            // 加入网络后启动定时器发送数据
            osal_start_timerEx( GenericApp_TaskID, GENERICAPP_SEND_MSG_EVT, GENERICAPP_SEND_MSG_TIMEOUT );
          }
          break;
        default:
          break;
      }
      osal_msg_deallocate( (uint8 *)MSGpkt );
      MSGpkt = (afIncomingMSGPacket_t *)osal_msg_receive( GenericApp_TaskID );
    }
    return (events ^ SYS_EVENT_MSG);
  }

  // 定时发送传感器数据任务
  if ( events & GENERICAPP_SEND_MSG_EVT )
  {
    GenericApp_Send_Sensor_Message();
    osal_start_timerEx( GenericApp_TaskID, GENERICAPP_SEND_MSG_EVT, GENERICAPP_SEND_MSG_TIMEOUT );
    return (events ^ GENERICAPP_SEND_MSG_EVT);
  }
  
  return 0;
}

static void GenericApp_ProcessZDOMsgs( zdoIncomingMsg_t *inMsg )
{
  switch ( inMsg->clusterID )
  {
    case End_Device_Bind_rsp:
      if ( ZDO_ParseBindRsp( inMsg ) == ZSuccess ) HalLedSet( HAL_LED_4, HAL_LED_MODE_ON );
      break;
    case Match_Desc_rsp:
      break;
  }
}

static void GenericApp_HandleKeys( uint8 shift, uint8 keys ) {}

static void GenericApp_MessageMSGCB( afIncomingMSGPacket_t *pkt )
{
  // 终端接收处理逻辑：判定头帧与编号，驱动物理继电器
  if(pkt->cmd.Data[0] == 0xAA && pkt->cmd.Data[1] == bianhaoID)
  {
      if(pkt->cmd.Data[2] == 1) { P1_3 = 1; } // 闭合继电器
      else { P1_3 = 0; }                      // 断开继电器
  }
}

// ================== 核心：感知层多维数据采集打包 ==================
void GenericApp_Send_Sensor_Message( void )
{
  char txBuffer[13]; // 12字节内容 + 1字节结束符'\0'
  uint8 temp_val = 0, hum_val = 0, pir_status = 0;
  uint16 gas_val = 0, light_val = 0;
  
  // 1. 获取温湿度 (处理成数字)
  DHT11();
  temp_val = wendu_shi * 10 + wendu_ge;
  hum_val = shidu_shi * 10 + shidu_ge;
  
  // 2. 获取有害气体与光强 ADC 值
  gas_val = myApp_ReadGasLevel();
  light_val = myApp_ReadLightLevel();
  
  // 3. 获取人体红外状态
  pir_status = (P0_5 == 0) ? 0 : 1; 
    
  // 4. 严谨的数据打包方案 (12字节极简帧)
  // %c (编号1位), %02d (温度2位), %02d (湿度2位), %03d (气体3位), %03d (光强3位), %d (PIR 1位)
  // 例："225601208001"
  sprintf(txBuffer, "%c%02d%02d%03d%03d%d", 
          bianhaoID, 
          temp_val, hum_val, 
          gas_val, 
          light_val, 
          pir_status);
          
  // 5. 无线上报至协调器
  AF_DataRequest( &GenericApp_DstAddr, &GenericApp_epDesc,
                  GenericApp_Sensor_CLUSTERID,
                  12, // 严格发送12个字节
                  (uint8 *)txBuffer,
                  &GenericApp_TransID,
                  AF_DISCV_ROUTE, AF_DEFAULT_RADIUS ) ;
}

// 保持你原有的硬件 ADC 驱动不变
uint16 myApp_ReadLightLevel( void )
{
  uint16 reading = 0;
  ADCCFG |= 0x40;
  ADCCON3 = 0x86;
  while (!(ADCCON1 & 0x80));
  ADCCFG &= (0x40 ^ 0xFF);
  reading = ADCH;
  reading |= (int16) (ADCH << 8); 
  reading >>= 8;
  return (reading);
} 

uint16 myApp_ReadGasLevel( void )
{
  uint16 reading = 0;
  ADCCFG |= 0x80;
  ADCCON3 = 0x87;
  while (!(ADCCON1 & 0x80));
  ADCCFG &= (0x80 ^ 0xFF);
  reading = ADCH;
  reading |= (int16) (ADCH << 8); 
  reading >>= 8;
  return (reading);
}
