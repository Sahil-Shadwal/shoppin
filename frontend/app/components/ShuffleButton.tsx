import { Sparkles } from "lucide-react";

interface ShuffleButtonProps {
  onShuffle: () => void;
  isLoading: boolean;
}

export default function ShuffleButton({ onShuffle, isLoading }: ShuffleButtonProps) {
  return (
    <button
      onClick={onShuffle}
      disabled={isLoading}
      className="fixed bottom-8 right-8 bg-red-600 text-white p-4 rounded-full shadow-2xl hover:shadow-red-500/50 transition-all duration-300 hover:scale-110 disabled:bg-gray-400 disabled:cursor-not-allowed z-50 flex items-center gap-2 group overflow-hidden hover:bg-red-700"
      title="Get fresh pins"
    >
      {/* Sparkle animations */}
      
      <div className="relative w-6 h-6">
        <Sparkles className="w-6 h-6 relative z-10" />

        {/* AI Sparkle animations - always visible */}
        <>
          {/* Sparkle 1 - top right */}
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-white rounded-full animate-sparkle1" />
          
          {/* Sparkle 2 - bottom left */}
          <span className="absolute -bottom-1 -left-1 w-1.5 h-1.5 bg-yellow-300 rounded-full animate-sparkle2" />
          
          {/* Sparkle 3 - top left */}
          <span className="absolute -top-0.5 -left-0.5 w-1 h-1 bg-pink-300 rounded-full animate-sparkle3" />
          
          {/* Sparkle 4 - bottom right */}
          <span className="absolute -bottom-0.5 -right-0.5 w-1.5 h-1.5 bg-purple-300 rounded-full animate-sparkle4" />
        </>
      </div>

      <span className="font-semibold hidden md:inline relative z-10">
        {isLoading ? 'Loading...' : 'More Ideas'}
      </span>

      <style jsx>{`
        @keyframes sparkle1 {
          0%, 100% { opacity: 0; transform: scale(0) translate(0, 0); }
          50% { opacity: 1; transform: scale(1) translate(4px, -4px); }
        }
        
        @keyframes sparkle2 {
          0%, 100% { opacity: 0; transform: scale(0) translate(0, 0); }
          50% { opacity: 1; transform: scale(1.2) translate(-4px, 4px); }
        }
        
        @keyframes sparkle3 {
          0%, 100% { opacity: 0; transform: scale(0) translate(0, 0); }
          50% { opacity: 1; transform: scale(0.8) translate(-3px, -3px); }
        }
        
        @keyframes sparkle4 {
          0%, 100% { opacity: 0; transform: scale(0) translate(0, 0); }
          50% { opacity: 1; transform: scale(1) translate(3px, 3px); }
        }
        
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .animate-sparkle1 {
          animation: sparkle1 2s ease-in-out infinite;
        }
        
        .animate-sparkle2 {
          animation: sparkle2 2s ease-in-out 0.5s infinite;
        }
        
        .animate-sparkle3 {
          animation: sparkle3 2s ease-in-out 1s infinite;
        }
        
        .animate-sparkle4 {
          animation: sparkle4 2s ease-in-out 1.5s infinite;
        }
        
        .animate-shimmer {
          animation: shimmer 3s ease-in-out infinite;
        }
      `}</style>
    </button>
  );
}