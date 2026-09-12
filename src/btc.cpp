#include <Arduino.h>
#include "btc.h"
#include "Bitcoin.h"
#include "Hash.h"
#include "Conversion.h"
#include "GlobalVARS.h"

extern sWallet myWallet;

//Dice entropy, same scheme as Coldcard: SHA-256 over the ASCII digits of the
//rolls. Nothing here comes from the device, and the user can reproduce it with
//  printf '3141...' | sha256sum
void entropyFromDice(const char * rolls, size_t nRolls, uint8_t out[32]){
  sha256((const uint8_t *)rolls, nRolls, out);
}

//Get MnemonicWords from coin data and calculate last word
void createSeed(int nWords, uint8_t * entropy){
  size_t len = nWords*4/3;
  if (len % 4 || len < 16 || len > 32) {
    return;
  }
  const char * mn = mnemonicFromEntropy(entropy, len);
  if (!mn) return;
  strncpy(myWallet.mnemonic, mn, sizeof(myWallet.mnemonic) - 1);
  myWallet.mnemonic[sizeof(myWallet.mnemonic) - 1] = '\0';

  //Kept so the user can check the words against the entropy they produced
  toHex(entropy, len, myWallet.entropyHex, sizeof(myWallet.entropyHex));
  for(char *p = myWallet.entropyHex; *p; p++){
    if(*p >= 'a' && *p <= 'z') *p -= 32;
  }

  // Extract account zpub and the FIRST RECEIVE address
  HDPrivateKey hd(myWallet.mnemonic, strlen(myWallet.mnemonic), "", 0);
  HDPrivateKey account = hd.derive("m/84'/0'/0'/");

  account.xpub(myWallet.xpub, sizeof(myWallet.xpub));
  // m/84'/0'/0'/0/0 - account.address() would be the account key itself,
  // which no wallet ever shows and cannot be used to cross-check the seed
  account.derive("0/0").address(myWallet.firstAddress, sizeof(myWallet.firstAddress));
}


