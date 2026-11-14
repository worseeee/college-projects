
#ifndef SMARTCABINET_ENDDEVICE_H
#define SMARTCABINET_ENDDEVICE_H

#ifdef __cplusplus
extern "C" {
#endif

#include "hal_types.h"


#define SMARTCABINET_ENDPOINT       10
#define SMARTCABINET_PROFID         0x0F08
#define SMARTCABINET_DEVICEID       0x0002
#define SMARTCABINET_DEVICE_VERSION 0
#define SMARTCABINET_FLAGS          0
#define SMARTCABINET_CLUSTERID      0x0001


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


extern void SmartCabinet_Init(uint8 task_id);
extern uint16 SmartCabinet_ProcessEvent(uint8 task_id, uint16 events);

#ifdef __cplusplus
}
#endif

#endif /* SMARTCABINET_ENDDEVICE_H */
