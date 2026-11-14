#ifndef SMARTCABINET_COORD_H
#define SMARTCABINET_COORD_H

#ifdef __cplusplus
extern "C" {
#endif

#include "hal_types.h"

#define SMARTCABINET_ENDPOINT       10
#define SMARTCABINET_PROFID         0x0F08
#define SMARTCABINET_DEVICEID       0x0001
#define SMARTCABINET_DEVICE_VERSION 0
#define SMARTCABINET_FLAGS          0
#define SMARTCABINET_CLUSTERID      0x0001

#define FRAME_HEADER    0xAA
#define FRAME_TAIL      0x55

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

typedef struct {
  uint8 header;     
  uint8 length;     
  uint8 node_id;    
  uint8 cmd;       
  uint8 status;    
  uint8 temperature; 
  uint8 humidity;    
  uint8 smoke_h;    
  uint8 smoke_l;      
  uint8 checksum;     
  uint8 tail;       
} UartFrame_t;

typedef struct {
  uint8 node_id;
  uint8 cmd;
  uint8 status;
  uint8 temperature;
  uint8 humidity;
  uint8 reserve;
  uint8 reserve_h;
  uint8 reserve_l;
} DataPacket_t;

extern void SmartCabinet_Init(byte task_id);
extern UINT16 SmartCabinet_ProcessEvent(byte task_id, UINT16 events);

#ifdef __cplusplus
}
#endif

#endif