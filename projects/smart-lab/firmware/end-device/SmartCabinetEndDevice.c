#include "OSAL.h"
#include "AF.h"
#include "ZDApp.h"
#include "ZDObject.h"
#include "ZDProfile.h"
#include "SmartCabinetEndDevice.h"
#include "DebugTrace.h"
#include "hal_drivers.h"
#include "hal_key.h"
#include "hal_led.h"
#include "hal_uart.h"
#include "hal_adc.h"
#include "hal_mcu.h"
#include <string.h>

#define HEARTBEAT_EVENT           0x0002
#define TEMP_COLLECT_EVENT        0x0004
#define JOIN_NETWORK_EVENT        0x0010
#define LED_BLINK_EVENT           0x0020
#define PIR_POLL_EVENT            0x0040
#define SMOKE_POLL_EVENT          0x0080

#define PIR_PIN_BIT     0x20
#define RELAY_LOCK      P1_3
#define LED_GREEN       P1_0
#define LED_RED         P1_4

#define DHT11_PIN       P1_1
#define DHT11_PIN_BIT   0x02

#define SMOKE_THRESHOLD         1200   
#define SMOKE_CLEAR_THRESHOLD   1000    

#define CMD_HEARTBEAT       0x01
#define CMD_PIR_DETECTED    0x02
#define CMD_BORROW_REQUEST  0x03
#define CMD_RETURN_REQUEST  0x04
#define CMD_OPEN_LOCK       0x10
#define CMD_CLOSE_LOCK      0x11
#define CMD_STATUS_QUERY    0x20
#define CMD_TEMP_HUMIDITY   0x30
#define CMD_SMOKE_ALARM     0x40
#define CMD_SMOKE_CLEAR     0x41
#define CMD_SMOKE_DATA      0x42

#define CABINET_IDLE        0x00
#define CABINET_BORROWED    0x01
#define CABINET_ALARM       0xFF

byte SmartCabinet_TaskID;
static uint8 cabinet_status = CABINET_IDLE;
static uint8 cabinet_id = 0x01;
static uint16 pir_trigger_count = 0;
static devStates_t SmartCabinet_NwkState = DEV_INIT;
static bool network_joined = FALSE;

static uint8 pir_last_state = 0;

static uint8 current_temperature = 0;
static uint8 current_humidity = 0;

static uint16 current_smoke_value = 0;
static bool smoke_alarm_active = FALSE;
static uint8 smoke_alarm_count = 0;

uint8 SmartCabinet_TransID = 0;

afAddrType_t Coordinator_DstAddr;

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

static void InitHardware(void);
static void InitSmokeADC(void);
static uint16 ReadSmokeSensor(void);
static uint8 ReadPIRSensor(void);
static void ProcessIncomingMessage(afIncomingMSGPacket_t *pkt);
static void PollPIRSensor(void);
static void PollSmokeSensor(void);
static void SendPIRData(void);
static void SendSmokeData(uint8 cmd_type, uint16 smoke_value);
static void OpenLock(void);
static void CloseLock(void);
static void CollectAndSendTempHumidity(void);
static void SendHeartbeat(void);
static void SendStatusReport(uint8 report_cmd);
static void SendDataToCoordinator(DataPacket_t *data);
static void Delay_us(uint16 us);
static void Delay_ms(uint16 ms);
static bool DHT11_Read(uint8 *temp, uint8 *humi);

static void Delay_us(uint16 us) {
  while (us--) {
    asm("NOP"); asm("NOP"); asm("NOP"); asm("NOP");
    asm("NOP"); asm("NOP"); asm("NOP"); asm("NOP");
  }
}

static void Delay_ms(uint16 ms) {
  while (ms--) {
    Delay_us(1000);
  }
}

static void InitSmokeADC(void) {

  P0SEL |= 0x80;      
  P0DIR &= ~0x80;   
  P0INP |= 0x80;    
  
  APCFG |= 0x80;    
}

static uint16 ReadSmokeSensor(void) {
  uint16 adc_value;
  
  P0SEL |= 0x80;      
  P0DIR &= ~0x80;    
  APCFG |= 0x80;     
  
  ADCCON3 = 0xB7;
  
  Delay_us(50);
  
  ADCCON1 |= 0x40;    
  
  while (!(ADCCON1 & 0x80)); 
  
  adc_value = ADCL;
  adc_value |= ((uint16)ADCH << 8);
  
  adc_value >>= 2;
  
  return adc_value;
}

static void PollSmokeSensor(void) {
  uint16 smoke_value;
  
  smoke_value = ReadSmokeSensor();
  current_smoke_value = smoke_value;
  
  if (network_joined) {
    SendSmokeData(CMD_SMOKE_DATA, smoke_value);
  }
  
  if (smoke_value > SMOKE_THRESHOLD) {
    smoke_alarm_count++;
    
    if (smoke_alarm_count >= 3 && !smoke_alarm_active) {
      smoke_alarm_active = TRUE;
      cabinet_status = CABINET_ALARM;
      
      LED_RED = 1;
      LED_GREEN = 0;
      
      if (network_joined) {
        SendSmokeData(CMD_SMOKE_ALARM, smoke_value);
      }
    }
  } 
  else if (smoke_value < SMOKE_CLEAR_THRESHOLD) {
    smoke_alarm_count = 0;
    
    if (smoke_alarm_active) {
      smoke_alarm_active = FALSE;
      cabinet_status = CABINET_IDLE;
      
      LED_RED = 0;
      LED_GREEN = 1;
      
      if (network_joined) {
        SendSmokeData(CMD_SMOKE_CLEAR, smoke_value);
      }
    }
  }
  
  if (smoke_alarm_active) {
    LED_RED = !LED_RED;
  }
}

static void SendSmokeData(uint8 cmd_type, uint16 smoke_value) {
  DataPacket_t data;
  
  data.node_id = cabinet_id;
  data.cmd = cmd_type;
  data.status = cabinet_status;
  data.temperature = current_temperature;
  data.humidity = current_humidity;
  data.reserve = 0;
  data.reserve_h = (uint8)(smoke_value >> 8);
  data.reserve_l = (uint8)(smoke_value & 0xFF);
  
  SendDataToCoordinator(&data);
}

static void DHT11_SetOutput(void) {
  P1SEL &= ~DHT11_PIN_BIT;
  P1DIR |= DHT11_PIN_BIT;
}

static void DHT11_SetInput(void) {
  P1SEL &= ~DHT11_PIN_BIT;
  P1DIR &= ~DHT11_PIN_BIT;
  P1INP |= DHT11_PIN_BIT;
}

static uint8 DHT11_ReadPin(void) {
  return (P1 & DHT11_PIN_BIT) ? 1 : 0;
}

static void DHT11_WritePin(uint8 val) {
  if (val) P1 |= DHT11_PIN_BIT;
  else P1 &= ~DHT11_PIN_BIT;
}

static bool DHT11_Read(uint8 *temp, uint8 *humi) {
  uint8 data[5] = {0};
  uint8 i;
  uint8 byte_idx, bit_idx;
  uint16 timeout;
  uint8 ea_save = EA;
  
  EA = 0;
  
  DHT11_SetOutput();
  DHT11_WritePin(0);
  Delay_ms(20);
  DHT11_WritePin(1);
  Delay_us(30);
  
  DHT11_SetInput();
  
  timeout = 100;
  while (DHT11_ReadPin() && timeout--) Delay_us(1);
  if (timeout == 0) { EA = ea_save; return FALSE; }
  
  timeout = 100;
  while (!DHT11_ReadPin() && timeout--) Delay_us(1);
  if (timeout == 0) { EA = ea_save; return FALSE; }
  
  timeout = 100;
  while (DHT11_ReadPin() && timeout--) Delay_us(1);
  if (timeout == 0) { EA = ea_save; return FALSE; }
  
  for (i = 0; i < 40; i++) {
    byte_idx = i / 8;
    bit_idx = 7 - (i % 8);
    
    timeout = 100;
    while (!DHT11_ReadPin() && timeout--) Delay_us(1);
    if (timeout == 0) { EA = ea_save; return FALSE; }
    
    Delay_us(30);
    
    if (DHT11_ReadPin()) {
      data[byte_idx] |= (1 << bit_idx);
      timeout = 100;
      while (DHT11_ReadPin() && timeout--) Delay_us(1);
    }
  }
  
  EA = ea_save;
  
  if (data[4] != ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) {
    return FALSE;
  }
  
  *humi = data[0];
  *temp = data[2];
  return TRUE;
}

static uint8 ReadPIRSensor(void) {
  P0SEL &= ~PIR_PIN_BIT;
  P0DIR &= ~PIR_PIN_BIT;
  P0INP |= PIR_PIN_BIT;
  return (P0 & PIR_PIN_BIT) ? 1 : 0;
}

void SmartCabinet_Init(uint8 task_id) {
  SmartCabinet_TaskID = task_id;
  
  Coordinator_DstAddr.addrMode = (afAddrMode_t)Addr16Bit;
  Coordinator_DstAddr.endPoint = SMARTCABINET_ENDPOINT;
  Coordinator_DstAddr.addr.shortAddr = 0x0000;
  
  SmartCabinet_epDesc.endPoint = SMARTCABINET_ENDPOINT;
  SmartCabinet_epDesc.task_id = &SmartCabinet_TaskID;
  SmartCabinet_epDesc.simpleDesc = (SimpleDescriptionFormat_t *)&SmartCabinet_SimpleDesc;
  SmartCabinet_epDesc.latencyReq = noLatencyReqs;
  
  afRegister(&SmartCabinet_epDesc);
  
  InitHardware();
  
  ZDOInitDevice(0);
  
  osal_start_timerEx(SmartCabinet_TaskID, LED_BLINK_EVENT, 500);
  osal_start_timerEx(SmartCabinet_TaskID, JOIN_NETWORK_EVENT, 30000);
  osal_start_timerEx(SmartCabinet_TaskID, PIR_POLL_EVENT, 3000);
  osal_start_timerEx(SmartCabinet_TaskID, SMOKE_POLL_EVENT, 1000);
}

static void InitHardware(void) {
  P1SEL &= ~0x1B;
  P1DIR |= 0x19;
  
  LED_GREEN = 0;
  LED_RED = 0;
  RELAY_LOCK = 0;
  
  InitSmokeADC();
  
  pir_last_state = ReadPIRSensor();
  
  DHT11_Read(&current_temperature, &current_humidity);
  current_smoke_value = ReadSmokeSensor();
}

static void SendPIRData(void) {
  DataPacket_t data;
  
  pir_trigger_count++;
  
  data.node_id = cabinet_id;
  data.cmd = CMD_PIR_DETECTED;
  data.status = cabinet_status;
  data.temperature = current_temperature;
  data.humidity = current_humidity;
  data.reserve = 0;
  data.reserve_h = (uint8)(pir_trigger_count >> 8);
  data.reserve_l = (uint8)(pir_trigger_count & 0xFF);
  
  SendDataToCoordinator(&data);
}

static void PollPIRSensor(void) {
  uint8 current_state;
  
  current_state = ReadPIRSensor();
  
  if (network_joined && !smoke_alarm_active) {
    LED_RED = current_state;
  }
  
  if (current_state == 1 && pir_last_state == 0) {
    if (!smoke_alarm_active) {
      LED_GREEN = 0; Delay_ms(50);
      LED_GREEN = 1; Delay_ms(50);
      LED_GREEN = 0; Delay_ms(50);
      LED_GREEN = 1; Delay_ms(50);
      LED_GREEN = 0; Delay_ms(50);
      LED_GREEN = 1;
    }
    
    if (network_joined) {
      SendPIRData();
    }
  }
  
  pir_last_state = current_state;
}

uint16 SmartCabinet_ProcessEvent(uint8 task_id, uint16 events) {
  afIncomingMSGPacket_t *MSGpkt;
  (void)task_id;
  
  if (events & SYS_EVENT_MSG) {
    MSGpkt = (afIncomingMSGPacket_t *)osal_msg_receive(SmartCabinet_TaskID);
    
    while (MSGpkt) {
      switch (MSGpkt->hdr.event) {
        case ZDO_STATE_CHANGE:
          SmartCabinet_NwkState = (devStates_t)(MSGpkt->hdr.status);
          
          if (SmartCabinet_NwkState == DEV_END_DEVICE ||
              SmartCabinet_NwkState == DEV_END_DEVICE_UNAUTH) {
            network_joined = TRUE;
            LED_GREEN = 1;
            LED_RED = 0;
            osal_stop_timerEx(SmartCabinet_TaskID, LED_BLINK_EVENT);
            
            SendHeartbeat();
            CollectAndSendTempHumidity();
            
            osal_start_timerEx(SmartCabinet_TaskID, HEARTBEAT_EVENT, 10000);
            osal_start_timerEx(SmartCabinet_TaskID, TEMP_COLLECT_EVENT, 3000);
          } 
          else {
            network_joined = FALSE;
            LED_GREEN = 0;
            LED_RED = 1;
          }
          break;
          
        case AF_INCOMING_MSG_CMD:
          if (network_joined) {
            ProcessIncomingMessage(MSGpkt);
          }
          break;
          
        default:
          break;
      }
      
      osal_msg_deallocate((uint8 *)MSGpkt);
      MSGpkt = (afIncomingMSGPacket_t *)osal_msg_receive(SmartCabinet_TaskID);
    }
    return (events ^ SYS_EVENT_MSG);
  }
  
  if (events & SMOKE_POLL_EVENT) {
    PollSmokeSensor();
    osal_start_timerEx(SmartCabinet_TaskID, SMOKE_POLL_EVENT, 1000);
    return (events ^ SMOKE_POLL_EVENT);
  }
  
  if (events & PIR_POLL_EVENT) {
    PollPIRSensor();
    osal_start_timerEx(SmartCabinet_TaskID, PIR_POLL_EVENT, 200);
    return (events ^ PIR_POLL_EVENT);
  }
  
  if (events & LED_BLINK_EVENT) {
    if (!network_joined) {
      LED_RED = !LED_RED;
      osal_start_timerEx(SmartCabinet_TaskID, LED_BLINK_EVENT, 500);
    }
    return (events ^ LED_BLINK_EVENT);
  }
  
  if (events & JOIN_NETWORK_EVENT) {
    if (!network_joined) {
      ZDOInitDevice(0);
      osal_start_timerEx(SmartCabinet_TaskID, JOIN_NETWORK_EVENT, 30000);
    }
    return (events ^ JOIN_NETWORK_EVENT);
  }
  
  if (events & HEARTBEAT_EVENT) {
    if (network_joined) {
      SendHeartbeat();
    }
    osal_start_timerEx(SmartCabinet_TaskID, HEARTBEAT_EVENT, 10000);
    return (events ^ HEARTBEAT_EVENT);
  }
  
  if (events & TEMP_COLLECT_EVENT) {
    if (network_joined) {
      CollectAndSendTempHumidity();
    }
    osal_start_timerEx(SmartCabinet_TaskID, TEMP_COLLECT_EVENT, 3000);
    return (events ^ TEMP_COLLECT_EVENT);
  }
  
  return 0;
}

static void SendDataToCoordinator(DataPacket_t *data) {
  if (!network_joined) return;
  
  AF_DataRequest(&Coordinator_DstAddr, 
                 &SmartCabinet_epDesc,
                 SMARTCABINET_CLUSTERID,
                 sizeof(DataPacket_t), 
                 (uint8 *)data,
                 &SmartCabinet_TransID,
                 AF_DISCV_ROUTE, 
                 AF_DEFAULT_RADIUS);
}

static void ProcessIncomingMessage(afIncomingMSGPacket_t *pkt) {
  DataPacket_t *rxData;
  
  if (pkt->cmd.DataLength < sizeof(DataPacket_t)) return;
  
  rxData = (DataPacket_t *)pkt->cmd.Data;
  
  if (rxData->node_id != cabinet_id && rxData->node_id != 0xFF) return;
  
  switch (rxData->cmd) {
    case CMD_OPEN_LOCK:
      OpenLock();
      cabinet_status = CABINET_BORROWED;
      LED_GREEN = 0;
      SendStatusReport(CMD_BORROW_REQUEST);
      break;
      
    case CMD_CLOSE_LOCK:
      CloseLock();
      cabinet_status = CABINET_IDLE;
      LED_GREEN = 1;
      SendStatusReport(CMD_RETURN_REQUEST);
      break;
      
    case CMD_STATUS_QUERY:
      CollectAndSendTempHumidity();
      SendSmokeData(CMD_SMOKE_DATA, current_smoke_value);
      break;
      
    default:
      break;
  }
}

static void OpenLock(void) {
  RELAY_LOCK = 1;
  LED_GREEN = 1; Delay_ms(200); LED_GREEN = 0; Delay_ms(200);
  LED_GREEN = 1;
}

static void CloseLock(void) {
  RELAY_LOCK = 0;
  LED_RED = 1; Delay_ms(300); LED_RED = 0;
}

static void CollectAndSendTempHumidity(void) {
  uint8 temp, humi;
  DataPacket_t data;
  
  if (DHT11_Read(&temp, &humi)) {
    current_temperature = temp;
    current_humidity = humi;
  }
  
  data.node_id = cabinet_id;
  data.cmd = CMD_TEMP_HUMIDITY;
  data.status = cabinet_status;
  data.temperature = current_temperature;
  data.humidity = current_humidity;
  data.reserve = 0;
  data.reserve_h = (uint8)(current_smoke_value >> 8);
  data.reserve_l = (uint8)(current_smoke_value & 0xFF);
  
  SendDataToCoordinator(&data);
}

static void SendHeartbeat(void) {
  DataPacket_t data;
  
  data.node_id = cabinet_id;
  data.cmd = CMD_HEARTBEAT;
  data.status = cabinet_status;
  data.temperature = current_temperature;
  data.humidity = current_humidity;
  data.reserve = 0;
  data.reserve_h = (uint8)(current_smoke_value >> 8);
  data.reserve_l = (uint8)(current_smoke_value & 0xFF);
  
  SendDataToCoordinator(&data);
}

static void SendStatusReport(uint8 report_cmd) {
  DataPacket_t data;
  
  data.node_id = cabinet_id;
  data.cmd = report_cmd;
  data.status = cabinet_status;
  data.temperature = current_temperature;
  data.humidity = current_humidity;
  data.reserve = 0;
  data.reserve_h = 0;
  data.reserve_l = 0;
  
  SendDataToCoordinator(&data);
}