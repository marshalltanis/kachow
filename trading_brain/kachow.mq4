//+------------------------------------------------------------------+
//|                                                       kachow.mq4 |
//|                                                   Copyright 2024
//|                          https://github.com/marshalltanis/kachow |
//+------------------------------------------------------------------+
#property link      "https://github.com/marshalltanis/kachow"
#property version   "1.00"
#property strict
#define SOCKET_LIBRARY_USE_EVENTS
#include <socket-library-mt4-mt5.mqh>

//+------------------------------------------------------------------+
//| Global Init                                   |
//+------------------------------------------------------------------+
ClientSocket *clientConnect;
ServerSocket *brokerConnect;
const ushort connectionPort = 666;
ushort tick_number = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   if (!brokerConnect){
      brokerConnect = new ServerSocket(connectionPort, true);
      printf("Able to connect on port: %d\n", connectionPort);
   }
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Socket Acitivty Triggering                                                     |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)
   {
      if (id == CHARTEVENT_KEYDOWN) {
         // May be a real key press, or a dummy notification
         // resulting from socket activity. If lparam matches
         // any .GetSocketHandle() then it's from a socket.
         // If not, it's a real key press. (If lparam>256 then
         // it's also pretty reliably a socket message rather 
         // than a real key press.)
         
         if (lparam == brokerConnect.GetSocketHandle()) {
            if(!clientConnect){
               clientConnect = brokerConnect.Accept();
               if(!clientConnect){
                  printf("Failed to create connection with client\n");
               }
               else {
                  printf("Primed and ready\n");
               }
            }
            else{
               printf("Multi-client coming in part two\n");
            }
         } else if (lparam == clientConnect.GetSocketHandle()) {
            // Activity on client socket
         } else {
            // Doesn't match a socket. Assume real key pres
         }
      }
   }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(clientConnect) delete clientConnect;
   if(brokerConnect) delete brokerConnect;
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   MqlTick last_tick;
   SymbolInfoTick(Symbol(), last_tick);
   int spread = MarketInfo(Symbol(), MODE_SPREAD);
   string info_to_send = StringFormat("time:%s , bid:%f , ask:%f , volume:%f , spread:%d\n\r" , last_tick.time, last_tick.bid, last_tick.ask, last_tick.volume, spread);
   if(clientConnect) 
   { 
      clientConnect.Send(info_to_send);
   } 
   else{
      printf(info_to_send);
   } 
  }
   
//+------------------------------------------------------------------+
//| Tester function                                                  |
//+------------------------------------------------------------------+
double OnTester()
  {
//---
   double ret=0.0;
//---

//---
   return(ret);
  }
//+------------------------------------------------------------------+
