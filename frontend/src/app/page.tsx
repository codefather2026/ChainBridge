export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          ChainBridge
        </h1>
        <p className="text-center text-lg mb-4">
          Trustless Cross-Chain Atomic Swaps on Stellar
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className="border rounded-lg p-6 hover:border-stellar-primary transition-colors">
            <h2 className="text-xl font-semibold mb-2">🔒 Trustless</h2>
            <p className="text-gray-600">
              Hash Time-Locked Contracts ensure atomic swaps without intermediaries
            </p>
          </div>
          
          <div className="border rounded-lg p-6 hover:border-stellar-primary transition-colors">
            <h2 className="text-xl font-semibold mb-2">⚡ Fast</h2>
            <p className="text-gray-600">
              Complete cross-chain swaps in minutes, not hours
            </p>
          </div>
          
          <div className="border rounded-lg p-6 hover:border-stellar-primary transition-colors">
            <h2 className="text-xl font-semibold mb-2">💰 Low Cost</h2>
            <p className="text-gray-600">
              Leverage Stellar&apos;s low transaction fees for affordable swaps
            </p>
          </div>
        </div>
        
        <div className="mt-12 text-center">
          <p className="text-gray-500">
            Multi-chain support: Stellar, Bitcoin, Ethereum, Solana, and more
          </p>
        </div>
      </div>
    </main>
  );
}
