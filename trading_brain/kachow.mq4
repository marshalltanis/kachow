//+------------------------------------------------------------------+
//|                                                       kachow.mq4 |
//|                                                   Copyright 2024
//|                          https://github.com/marshalltanis/kachow |
//+------------------------------------------------------------------+
#property link      "https://github.com/marshalltanis/kachow"
#property version   "1.00"
#property strict
#include <socket-library-mt4-mt5.mqh>

//+------------------------------------------------------------------+
//| Global Init                                   |
//+------------------------------------------------------------------+
ClientSocket *clientConnect;
ServerSocket *brokerConnect;
const ushort connectionPort = 666;
ushort tick_number = 0;
string ConfigFile = "EURUSD15.csv"; // Name of the configuration file
int TickInterval = 1;                       // Interval in seconds for simulated ticks

// Global variables
bool isMarketClosed = false;

int handle = INVALID_HANDLE; // File handle (global variable)
int lineIndex = 0;
double bidPrice = 0.0;
double askPrice = 0.0;           // Current line index (global variable)
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   if (!brokerConnect){
      brokerConnect = new ServerSocket(connectionPort, true);
      printf("Able to connect on port: %d\n", connectionPort);
   }
   CheckMarketStatus();
   if(isMarketClosed){
      EventSetTimer(TickInterval); // Set timer to trigger every `TickInterval` seconds
      handle = FileOpen(ConfigFile, FILE_CSV | FILE_READ);
      if (handle == INVALID_HANDLE)
       {
           Print("Error: Unable to open file.");
       }
   }
   else{
      #define SOCKET_LIBRARY_USE_EVENTS
   }
   MathSrand(GetTickCount());
   
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
            printf("Found activity on client socket\n");
            // Activity on client socket
         } else {
            printf("Maybe I'm in here?");
            // Doesn't match a socket. Assume real key pres
         }
      }
      else{
         printf("%d is the ID");
      }
   }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(clientConnect) delete clientConnect;
   if(brokerConnect) delete brokerConnect;
   EventKillTimer(); // Stop the timer when EA is removed
  }
//+------------------------------------------------------------------+
//| Timer Event                                                      |
//+------------------------------------------------------------------+
void OnTimer()
{
    if (!isMarketClosed)
    {
        Print("Market is open, skipping simulated tick.");
        return; // Exit if market is open
    }
    while(!clientConnect){
      clientConnect = brokerConnect.Accept();
    }
    printf("primed");

    // Simulate a tick
    SimulateTick();
}

//+------------------------------------------------------------------+
//| Check Market Status                                              |
//+------------------------------------------------------------------+
void CheckMarketStatus()
{
    // Example: Use market hours or MarketInfo() to determine if market is closed
    datetime currentTime = TimeCurrent();
    int dayOfWeek = TimeDayOfWeek(currentTime);
    // Assume market is closed on weekends
    if (dayOfWeek == 0 || dayOfWeek == 6)
        isMarketClosed = true;
    else
        isMarketClosed = false;
}
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   MqlTick last_tick;
   SymbolInfoTick(Symbol(), last_tick);
   double spread = MarketInfo(Symbol(), MODE_SPREAD);
   double open = iOpen(Symbol(), Period(), 0);
   double close = iClose(Symbol(), Period(), 0);
   string info_to_send = StringFormat("time:%s , bid:%f , ask:%f , volume:%f , spread:%d , open:%f , close:%f \n\r" , last_tick.time, last_tick.bid, last_tick.ask, last_tick.volume, spread, open, close);
   SendTick(info_to_send);
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

//+------------------------------------------------------------------+
//| Simulate Tick Logic                                              |
//+------------------------------------------------------------------+
void SimulateTick()
{
    string time;
    string open;
    string high;
    string low;
    string close;
    string volume;
    string spread;
    if (handle == INVALID_HANDLE)
    {
        Print("Error: File not open.");
        return;
    }
    // Move to the current line index
    for (int i = 0; i < lineIndex; i++)
    {
        if (FileIsEnding(handle)) break;
        FileReadString(handle); // Skip lines
    }

     string line = FileReadString(handle);
     if (StringLen(line) > 0)
     {
         // Example format: price,volume
         string ticks[];
         StringSplit(line, ',', ticks);
         if(ArraySize(ticks) < 7){
            printf("Incomplete line found\n");
            return;
         }
         printf(line);
         time = StringFormat("%sT%s", ticks[0], ticks[1]);
         open = ticks[2];
         high = ticks[3];
         low = ticks[4];
         close = ticks[5];
         volume = ticks[6];
         spread = "0.0009";
         GenerateRandomPrices(StringToDouble(low), StringToDouble(high), StringToDouble(spread));
         string info_to_send = StringFormat("time:%s , bid:%f , ask:%f , volume:%s , spread:%s , open:%s , close:%s \n\r" , time, bidPrice, askPrice, volume, spread, open, close);
         SendTick(info_to_send);

    }
    lineIndex++;
}


//+------------------------------------------------------------------+
//| Process Tick                                           |
//+------------------------------------------------------------------+
void SendTick(string info_to_send)
{
   if(clientConnect) 
   { 
      if(clientConnect.IsSocketConnected()){
         printf("Sending data %s\n",info_to_send);
         clientConnect.Send(info_to_send);
      }
      else {
         // Create disconnect function at some point
         printf("Socket is closed, waiting for new connection");
         clientConnect = NULL;
      }
   } 
   else{
      printf(info_to_send);
   }
}

// Generate random bid and ask prices within a specified range
void GenerateRandomPrices(double minPrice, double maxPrice, double spread)
{

    // Generate random bid price
    bidPrice = minPrice + MathRand() * (maxPrice - minPrice) / 32767.0;

    // Ensure ask price is always higher than bid
    askPrice = bidPrice + spread + MathRand() * (spread * 2) / 32767.0;

    Print("Random Bid: ", bidPrice, ", Random Ask: ", askPrice);
}