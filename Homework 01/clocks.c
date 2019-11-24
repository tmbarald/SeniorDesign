// ------------------------------------------------------------------------------
//
//  Description: This file contains the Clock Initialization
//
//  Jim Carlson
//  Jan 2016
//  Built with IAR Embedded Workbench Version: V7.12.1
// ------------------------------------------------------------------------------
#include  "functions.h"
#include  "msp430.h"

// MACROS========================================================================
#define MCLK_FREQ_MHZ 8                     // MCLK = 8MHz
#define CLEAR_REGISTER     (0X0000)

void Init_Clocks(void);
void Software_Trim(void);

void Init_Clocks(void){
// -----------------------------------------------------------------------------
// Clock Configurtaions
// This is the clock initialization for the program.
// Initial clock configuration, runs immediately after port configuration.
// Disables 1ms watchdog timer,
// Configure MCLK for 8MHz and XT1 sourcing ACLK and FLLREF.
//
// Description: Configure ACLK = 32768Hz,
//                        MCLK = DCO + XT1CLK REF = 8MHz,
//                        SMCLK = MCLK/2 = 4MHz.
// Toggle LED to indicate that the program is running.
//
// -----------------------------------------------------------------------------
  WDTCTL = WDTPW | WDTHOLD;  // Disable watchdog

  do{
    CSCTL7 &= ~XT1OFFG;      // Clear XT1 fault flag
    CSCTL7 &= ~DCOFFG;       // Clear DCO fault flag
    SFRIFG1 &= ~OFIFG;
  } while (SFRIFG1 & OFIFG); // Test oscillator fault flag
  __bis_SR_register(SCG0);   // disable FLL

  CSCTL1 = DCOFTRIMEN_1;
  CSCTL1 |= DCOFTRIM0;
  CSCTL1 |= DCOFTRIM1;       // DCOFTRIM=3
  CSCTL1 |= DCORSEL_3;       // DCO Range = 8MHz

  CSCTL2 = FLLD_0 + 243;     // DCODIV = 8MHz

  CSCTL3 |= SELREF__XT1CLK;  // Set XT1CLK as FLL reference source
  __delay_cycles(3);
  __bic_SR_register(SCG0);   // enable FLL
  Software_Trim();           // Software Trim to get the best DCOFTRIM value

  CSCTL4 = SELA__XT1CLK;     // Set ACLK = XT1CLK = 32768Hz
  CSCTL4 |= SELMS__DCOCLKDIV;// DCOCLK = MCLK and SMCLK source

  CSCTL5 |= DIVM_0;          // MCLK = DCOCLK = 8MHZ,
  CSCTL5 |= DIVS_0;          // SMCLK = DCOCLK = 8MHz

  PM5CTL0 &= ~LOCKLPM5;      // Disable the GPIO power-on default high-impedance mode
                             // to activate previously configured port settings
}

void Software_Trim(void){
// --COPYRIGHT--,BSD_EX
// Copyright (c) 2014, Texas Instruments Incorporated
// All rights reserved.
  unsigned int oldDcoTap = 0xffff;
  unsigned int newDcoTap = 0xffff;
  unsigned int newDcoDelta = 0xffff;
  unsigned int bestDcoDelta = 0xffff;
  unsigned int csCtl0Copy = 0;
  unsigned int csCtl1Copy = 0;
  unsigned int csCtl0Read = 0;
  unsigned int csCtl1Read = 0;
  unsigned int dcoFreqTrim = 3;
  unsigned char endLoop = 0;
  do{
    CSCTL0 = 0x100;                         // DCO Tap = 256
    do{
      CSCTL7 &= ~DCOFFG;                    // Clear DCO fault flag
    }while (CSCTL7 & DCOFFG);               // Test DCO fault flag
    // Wait FLL lock status (FLLUNLOCK) to be stable
    // Suggest to wait 24 cycles of divided FLL reference clock
    __delay_cycles((unsigned int)3000 * MCLK_FREQ_MHZ);
    while((CSCTL7 & (FLLUNLOCK0 | FLLUNLOCK1)) &&
         ((CSCTL7 & DCOFFG) == 0));
    csCtl0Read = CSCTL0;                    // Read CSCTL0
    csCtl1Read = CSCTL1;                    // Read CSCTL1
    oldDcoTap = newDcoTap;                  // Record DCOTAP value of last time
    newDcoTap = csCtl0Read & 0x01ff;        // Get DCOTAP value of this time
    dcoFreqTrim = (csCtl1Read & 0x0070)>>4; // Get DCOFTRIM value
    if(newDcoTap < 256){                    // DCOTAP < 256
      newDcoDelta = 256 - newDcoTap;        // Delta value between DCPTAP and 256
      if((oldDcoTap != 0xffff) &&
         (oldDcoTap >= 256)){               // DCOTAP cross 256
        endLoop = 1;                        // Stop while loop
      }else{
        dcoFreqTrim--;
        CSCTL1 = (csCtl1Read & (~DCOFTRIM)) | (dcoFreqTrim<<4);
      }
    }else{                                  // DCOTAP >= 256
      newDcoDelta = newDcoTap - 256;        // Delta value between DCPTAP and 256
      if(oldDcoTap < 256){                  // DCOTAP cross 256
        endLoop = 1;                        // Stop while loop
      }else{
        dcoFreqTrim++;
        CSCTL1 = (csCtl1Read & (~DCOFTRIM)) | (dcoFreqTrim<<4);
      }
    }
    if(newDcoDelta < bestDcoDelta){         // Record DCOTAP closest to 256
      csCtl0Copy = csCtl0Read;
      csCtl1Copy = csCtl1Read;
      bestDcoDelta = newDcoDelta;
    }
  }while(endLoop == 0);                     // Poll until endLoop == 1
  CSCTL0 = csCtl0Copy;                      // Reload locked DCOTAP
  CSCTL1 = csCtl1Copy;                      // Reload locked DCOFTRIM
  while(CSCTL7 & (FLLUNLOCK0 | FLLUNLOCK1));// Poll until FLL is locked
}


