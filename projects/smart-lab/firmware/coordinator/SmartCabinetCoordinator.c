#include "OSAL.h"
#include "AF.h"
#include "ZDApp.h"
#include "ZDObject.h"
#include "ZDProfile.h"
#include "SmartCabinetCoordinator.h"
#include "DebugTrace.h"
#include "hal_drivers.h"
#include "hal_key.h"
#include "hal_led.h"
#include "hal_uart.h"
#include <string.h>


#define COORD_TEST_EVENT    0x0010


byte SmartCabinet_TaskID;
uint8 SmartCabinet_TransID = 0;
static devStates_t SmartCabinet_NwkState = DEV_INIT;

static uint8 uart_rx_buffer[128];
static uint8 uart_rx_index = 0;


#define MAX_END_DEVICES 10
typedef struct {
  uint8 node_id;
  uint16 short_addr;
  uint8 online;
} EndDeviceInfo_t;

static EndDeviceInfo_t endDeviceList[MAX_END_DEVICES];
static uint8 endDeviceCount = 0;


const cId_t SmartCabinet_ClusterList[1] = { SMARTCABINET_CLUSTERID };

const SimpleDescriptionFormat_t SmartCabinet_SimpleDesc = {
  SMARTCABINET_ENDPOINT,
  SMARTCABINET_PROFID,
  SMARTCABINET_DEVICEID,
  SMARTCABINET_DEVICE_VERSION,
  SMARTCABINET_FLAGS,
  1,
  (cId_t *)SmartCabinet_ClusterList,
  1,
  (cId_t *)SmartCabinet_ClusterList
};

endPointDesc_t SmartCabinet_epDesc;

static afAddrType_t Broadcast_DstAddr;
static afAddrType_t Point_To_Point_DstAddr;


static void InitUart(void);
static void UartRxCallback(uint8 port, uint8 event);
static bool VerifyChecksum(UartFrame_t *frame);
static void ProcessUartCommand(UartFrame_t *frame);
static void ProcessZigBeeMessage(afIncomingMSGPacket_t *pkt);
static uint16 GetShortAddrByNodeID(uint8 node_id);
static void RegisterEndDevice(uint8 node_id, uint16 short_addr);
static void SendTestToUart(void);


void SmartCabinet_Init(byte task_id) {
  SmartCabinet_TaskID = task_id;
  
  Broadcast_DstAddr.addrMode = (afAddrMode_t)AddrBroadcast;
  Broadcast_DstAddr.endPoint = SMARTCABINET_ENDPOINT;
  Broadcast_DstAddr.addr.shortAddr = 0xFFFF;
  
  Point_To_Point_DstAddr.addrMode = (afAddrMode_t)Addr16Bit;
  Point_To_Point_DstAddr.endPoint = SMARTCABINET_ENDPOINT;
  Point_To_Point_DstAddr.addr.shortAddr = 0x0000;
  
  SmartCabinet_epDesc.endPoint = SMARTCABINET_ENDPOINT;
  SmartCabinet_epDesc.task_id = &SmartCabinet_TaskID;
  SmartCabinet_epDesc.simpleDesc = (SimpleDescriptionFormat_t *)&SmartCabinet_SimpleDesc;
  SmartCabinet_epDesc.latencyReq = noLatencyReqs;
  
  afRegister(&SmartCabinet_epDesc);
  
  InitUart();
  
  osal_memset(endDeviceList, 0, sizeof(endDeviceList));
  endDeviceCount = 0;
  
  ZDOInitDevice(0);
  
  HalLedSet(HAL_LED_1, HAL_LED_MODE_ON);
  
  osal_start_timerEx(SmartCabinet_TaskID, COORD_TEST_EVENT, 3000);
}


static void InitUart(void) {
  halUARTCfg_t uartConfig;
  
  osal_memset(&uartConfig, 0, sizeof(halUARTCfg_t));
  
  uartConfig.configured = TRUE;
  uartConfig.baudRate = HAL_UART_BR_115200;
  uartConfig.flowControl = FALSE;
  uartConfig.flowControlThreshold = 64;
  uartConfig.rx.maxBufSize = 128;
  uartConfig.tx.maxBufSize = 128;
  uartConfig.idleTimeout = 6;
  uartConfig.intEnable = TRUE;
  uartConfig.callBackFunc = UartRxCallback;
  
  HalUARTOpen(HAL_UART_PORT_0, &uartConfig);
  
  HalUARTWrite(HAL_UART_PORT_0, (uint8 *)"Coord OK\r\n", 10);
}


static void SendTestToUart(void) {
  UartFrame_t testFrame;
  uint8 i;
  uint8 *p;
  
  testFrame.header = FRAME_HEADER;
  testFrame.length = 7;  
  testFrame.node_id = 0x00;
  testFrame.cmd = CMD_HEARTBEAT;
  testFrame.status = (SmartCabinet_NwkState == DEV_ZB_COORD) ? 0x01 : 0x00;
  testFrame.temperature = 25;
  testFrame.humidity = 60;
  testFrame.smoke_h = 0;
  testFrame.smoke_l = 0;
  
  
  p = (uint8 *)&testFrame;
  testFrame.checksum = 0;
  for (i = 0; i < sizeof(UartFrame_t) - 2; i++) {
    testFrame.checksum += p[i];
  }
  testFrame.tail = FRAME_TAIL;
  
  HalUARTWrite(HAL_UART_PORT_0, (uint8 *)&testFrame, sizeof(UartFrame_t));
}


static void UartRxCallback(uint8 port, uint8 event) {
  uint8 ch;
  (void)port;
  (void)event;
  
  while (Hal_UART_RxBufLen(HAL_UART_PORT_0) > 0) {
    HalUARTRead(HAL_UART_PORT_0, &ch, 1);
    
    if (uart_rx_index == 0) {
      if (ch == FRAME_HEADER) {
        uart_rx_buffer[uart_rx_index++] = ch;
      }
    }
    else if (uart_rx_index < sizeof(UartFrame_t)) {
      uart_rx_buffer[uart_rx_index++] = ch;
      
      if (uart_rx_index == sizeof(UartFrame_t)) {
        UartFrame_t *frame = (UartFrame_t *)uart_rx_buffer;
        
        if (frame->tail == FRAME_TAIL && VerifyChecksum(frame)) {
          ProcessUartCommand(frame);
        }
        uart_rx_index = 0;
      }
    }
    else {
      uart_rx_index = 0;
    }
  }
}


static bool VerifyChecksum(UartFrame_t *frame) {
  uint8 sum = 0;
  uint8 i;
  uint8 *p = (uint8 *)frame;
  
  for (i = 0; i < sizeof(UartFrame_t) - 2; i++) {
    sum += p[i];
  }
  return (sum == frame->checksum);
}


static void ProcessUartCommand(UartFrame_t *frame) {
  DataPacket_t zigbee_data;
  uint16 shortAddr;
  
  zigbee_data.node_id = frame->node_id;
  zigbee_data.cmd = frame->cmd;
  zigbee_data.status = frame->status;
  zigbee_data.temperature = frame->temperature;
  zigbee_data.humidity = frame->humidity;
  zigbee_data.reserve = 0;
  zigbee_data.reserve_h = frame->smoke_h;
  zigbee_data.reserve_l = frame->smoke_l;

  if (frame->node_id == 0xFF) {
    AF_DataRequest(&Broadcast_DstAddr, &SmartCabinet_epDesc, SMARTCABINET_CLUSTERID,
                   sizeof(DataPacket_t), (uint8 *)&zigbee_data, &SmartCabinet_TransID,
                   AF_DISCV_ROUTE, AF_DEFAULT_RADIUS);
  }
  else {
    shortAddr = GetShortAddrByNodeID(frame->node_id);
    if (shortAddr != 0xFFFF) {
      Point_To_Point_DstAddr.addr.shortAddr = shortAddr;
      AF_DataRequest(&Point_To_Point_DstAddr, &SmartCabinet_epDesc, SMARTCABINET_CLUSTERID,
                     sizeof(DataPacket_t), (uint8 *)&zigbee_data, &SmartCabinet_TransID,
                     AF_DISCV_ROUTE, AF_DEFAULT_RADIUS);
    }
  }
  
  HalLedBlink(HAL_LED_2, 1, 50, 100);
}


UINT16 SmartCabinet_ProcessEvent(byte task_id, UINT16 events) {
  afIncomingMSGPacket_t *MSGpkt;
  (void)task_id;
  
  if (events & SYS_EVENT_MSG) {
    MSGpkt = (afIncomingMSGPacket_t *)osal_msg_receive(SmartCabinet_TaskID);
    
    while (MSGpkt) {
      switch (MSGpkt->hdr.event) {
        case ZDO_STATE_CHANGE:
          SmartCabinet_NwkState = (devStates_t)(MSGpkt->hdr.status);
          
          if (SmartCabinet_NwkState == DEV_ZB_COORD) {
            HalLedBlink(HAL_LED_1, 5, 50, 200);
            HalUARTWrite(HAL_UART_PORT_0, (uint8 *)"Net OK\r\n", 8);
          }
          break;
          
        case AF_INCOMING_MSG_CMD:
          ProcessZigBeeMessage(MSGpkt);
          break;
          
        default:
          break;
      }
      
      osal_msg_deallocate((uint8 *)MSGpkt);
      MSGpkt = (afIncomingMSGPacket_t *)osal_msg_receive(SmartCabinet_TaskID);
    }
    return (events ^ SYS_EVENT_MSG);
  }
  
  if (events & COORD_TEST_EVENT) {
    SendTestToUart();
    osal_start_timerEx(SmartCabinet_TaskID, COORD_TEST_EVENT, 10000);
    return (events ^ COORD_TEST_EVENT);
  }
  
  return 0;
}


static void ProcessZigBeeMessage(afIncomingMSGPacket_t *pkt) {
  DataPacket_t *rxData;
  UartFrame_t uart_frame;
  uint8 i;
  uint8 *p;
  
  if (pkt->cmd.DataLength < sizeof(DataPacket_t)) {
    return;
  }
  
  rxData = (DataPacket_t *)pkt->cmd.Data;
  
  RegisterEndDevice(rxData->node_id, pkt->srcAddr.addr.shortAddr);
  
  
  uart_frame.header = FRAME_HEADER;
  uart_frame.length = 7;
  uart_frame.node_id = rxData->node_id;
  uart_frame.cmd = rxData->cmd;
  uart_frame.status = rxData->status;
  uart_frame.temperature = rxData->temperature;
  uart_frame.humidity = rxData->humidity;
  uart_frame.smoke_h = rxData->reserve_h;    
  uart_frame.smoke_l = rxData->reserve_l;    

  
  p = (uint8 *)&uart_frame;
  uart_frame.checksum = 0;
  for (i = 0; i < sizeof(UartFrame_t) - 2; i++) {
    uart_frame.checksum += p[i];
  }
  uart_frame.tail = FRAME_TAIL;

  HalUARTWrite(HAL_UART_PORT_0, (uint8 *)&uart_frame, sizeof(UartFrame_t));
  HalLedBlink(HAL_LED_1, 2, 50, 100);
}


static void RegisterEndDevice(uint8 node_id, uint16 short_addr) {
  uint8 i;
  
  for (i = 0; i < endDeviceCount; i++) {
    if (endDeviceList[i].node_id == node_id) {
      endDeviceList[i].short_addr = short_addr;
      endDeviceList[i].online = 1;
      return;
    }
  }
  
  if (endDeviceCount < MAX_END_DEVICES) {
    endDeviceList[endDeviceCount].node_id = node_id;
    endDeviceList[endDeviceCount].short_addr = short_addr;
    endDeviceList[endDeviceCount].online = 1;
    endDeviceCount++;
  }
}

static uint16 GetShortAddrByNodeID(uint8 node_id) {
  uint8 i;
  
  for (i = 0; i < endDeviceCount; i++) {
    if (endDeviceList[i].node_id == node_id && endDeviceList[i].online) {
      return endDeviceList[i].short_addr;
    }
  }
  return 0xFFFF;
}
