#include "OSAL.h"
#include "AF.h"
#include "ZDApp.h"
#include "ZDObject.h"
#include "ZDProfile.h"
#include "GenericApp.h"
#include "DebugTrace.h"

#if !defined( WIN32 )
  #include "OnBoard.h"
#endif

/* HAL */
#include "hal_lcd.h"
#include "hal_led.h"
#include "hal_key.h"
#include "hal_uart.h"

const cId_t GenericApp_ClusterList[GENERICAPP_MAX_CLUSTERS] =
{
  GENERICAPP_CLUSTERID,
  GenericApp_Sensor_CLUSTERID // 确保加入了 Sensor 集簇
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

static void GenericApp_ProcessZDOMsgs( zdoIncomingMsg_t *inMsg );
static void GenericApp_HandleKeys( byte shift, byte keys );
static void GenericApp_MessageMSGCB( afIncomingMSGPacket_t *pckt );
static void GenericApp_UART_CB(uint8 port, uint8 event);

void GenericApp_Init( uint8 task_id )
{
  GenericApp_TaskID = task_id;
  GenericApp_NwkState = DEV_INIT;
  GenericApp_TransID = 0;

  GenericApp_DstAddr.addrMode = (afAddrMode_t)AddrBroadcast;
  GenericApp_DstAddr.endPoint = GENERICAPP_ENDPOINT;
  GenericApp_DstAddr.addr.shortAddr = 0xFFFF;
  
  // 串口配置
  halUARTCfg_t uartConfig;
  uartConfig.configured = TRUE;
  uartConfig.baudRate = HAL_UART_BR_115200;
  uartConfig.flowControl = FALSE;
  uartConfig.flowControlThreshold = 48;
  uartConfig.rx.maxBufSize = 128;
  uartConfig.tx.maxBufSize = 128;
  uartConfig.idleTimeout = 6;
  uartConfig.intEnable = TRUE;
  uartConfig.callBackFunc = GenericApp_UART_CB; 
  HalUARTOpen(0, &uartConfig);

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
          break;
        default:
          break;
      }
      osal_msg_deallocate( (uint8 *)MSGpkt );
      MSGpkt = (afIncomingMSGPacket_t *)osal_msg_receive( GenericApp_TaskID );
    }
    return (events ^ SYS_EVENT_MSG);
  }
  return 0;
}

static void GenericApp_ProcessZDOMsgs( zdoIncomingMsg_t *inMsg )
{
  switch ( inMsg->clusterID )
  {
    case End_Device_Bind_rsp:
      if ( ZDO_ParseBindRsp( inMsg ) == ZSuccess )
        HalLedSet( HAL_LED_4, HAL_LED_MODE_ON );
      break;
    case Match_Desc_rsp:
      {
        ZDO_ActiveEndpointRsp_t *pRsp = ZDO_ParseEPListRsp( inMsg );
        if ( pRsp && pRsp->status == ZSuccess && pRsp->cnt )
        {
          GenericApp_DstAddr.addrMode = (afAddrMode_t)Addr16Bit;
          GenericApp_DstAddr.addr.shortAddr = pRsp->nwkAddr;
          GenericApp_DstAddr.endPoint = pRsp->epList[0];
          HalLedSet( HAL_LED_4, HAL_LED_MODE_ON );
        }
        if(pRsp) osal_mem_free( pRsp );
      }
      break;
  }
}

static void GenericApp_HandleKeys( uint8 shift, uint8 keys ) { }

static void GenericApp_MessageMSGCB( afIncomingMSGPacket_t *pkt )
{
  switch ( pkt->clusterId )
  {
      // 核心业务：接收终端打好包的 12 字节数据，直接透传给上位机
      case GenericApp_Sensor_CLUSTERID:
        HalUARTWrite(0, pkt->cmd.Data, pkt->cmd.DataLength);
        break;
      
      default:
        break;
  }
}

// 协调器串口接收状态机，拦截 Python 下发的 "R:<NodeID>:<0/1>" (如 R:1:1)
static void GenericApp_UART_CB(uint8 port, uint8 event)
{
  uint8 ch;
  static uint8 rx_state = 0;
  static uint8 target_node = 0; // 缓存解析到的目标节点编号

  while (HalUARTRead(port, &ch, 1))
  {
    if (rx_state == 0 && ch == 'R') { rx_state = 1; }
    else if (rx_state == 1 && ch == ':') { rx_state = 2; }
    else if (rx_state == 2) // 阶段2：读取节点号 (如 '1' 或 '2')
    {
      target_node = ch; // 记录下是要控制哪个节点
      rx_state = 3;
    }
    else if (rx_state == 3 && ch == ':') { rx_state = 4; }
    else if (rx_state == 4) // 阶段4：读取控制位 ('0' 或 '1')
    {
      if (ch == '0' || ch == '1')
      {
        uint8 payload[3];
        payload[0] = 0xAA;              // 协议头 (0xAA)
        payload[1] = target_node;       // 动态填入目标节点编号
        payload[2] = ch - '0';          // 控制状态位: 0 或 1

        // 将控制指令通过 ZigBee 广播发送给所有终端节点
        // 终端节点的 GenericApp_MessageMSGCB 会自己根据 payload[1] 判断是否属于自己
        AF_DataRequest(&GenericApp_DstAddr, &GenericApp_epDesc,
                       GENERICAPP_CLUSTERID, 3, payload,
                       &GenericApp_TransID, AF_DISCV_ROUTE, AF_DEFAULT_RADIUS);
      }
      rx_state = 0; // 一条完整的指令解析完成，状态机复位
    }
    else 
    { 
      rx_state = 0; // 收到异常字符，状态机复位，防止卡死
    }
  }
}