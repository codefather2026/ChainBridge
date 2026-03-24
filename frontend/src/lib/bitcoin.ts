import * as bitcoin from "bitcoinjs-lib";

export function getBitcoinNetwork(): bitcoin.Network {
  if (process.env.NEXT_PUBLIC_BITCOIN_NETWORK === "mainnet") {
    return bitcoin.networks.bitcoin;
  }
  return bitcoin.networks.testnet;
}

export function createBitcoinAddress(publicKey: Buffer): string {
  const network = getBitcoinNetwork();
  const { address } = bitcoin.payments.p2wpkh({
    pubkey: publicKey,
    network,
  });
  return address || "";
}

export function validateBitcoinAddress(address: string): boolean {
  try {
    const network = getBitcoinNetwork();
    bitcoin.address.toOutputScript(address, network);
    return true;
  } catch {
    return false;
  }
}
