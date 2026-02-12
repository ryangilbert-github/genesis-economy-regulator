import { useState, useEffect } from 'react';
import axios from 'axios';
import { Scroll, Coins, ShieldAlert, Gift, Loader2, Play } from 'lucide-react';

function App() {
  const [quest, setQuest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Function to fetch the current quest from the DB
  const fetchQuest = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/current-quest');
      setQuest(response.data);
      setError(null);
    } catch (err) {
      console.error("API Error:", err);
      setError("Failed to contact the Genesis Archives.");
    } finally {
      setLoading(false);
    }
  };

  // Run on first load
  useEffect(() => {
    fetchQuest();
  }, []);

  // Function to trigger the Python simulation logic
  const triggerSimulation = async () => {
    setIsSimulating(true);
    try {
      // Hits the @app.post("/run-simulation") route we added to api.py
      await axios.post('http://127.0.0.1:8000/run-simulation');
      // Refresh the quest data once the simulation finishes
      await fetchQuest();
    } catch (err) {
      console.error("Sim Error:", err);
      setError("The simulation encountered a temporal rift (Error).");
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center p-4 font-mono">
      <div className="max-w-2xl w-full bg-slate-800 border-2 border-slate-700 rounded-lg shadow-2xl overflow-hidden animate-fade-in">

        {/* Header */}
        <div className="bg-slate-950 p-6 border-b border-slate-700 flex items-center gap-3">
          <ShieldAlert className="w-8 h-8 text-amber-500" />
          <div>
            <h1 className="text-2xl font-bold tracking-widest text-amber-500 uppercase">
              Genesis Economy Regulator
            </h1>
            <p className="text-xs text-slate-500">SYSTEM STATUS: ONLINE</p>
          </div>
        </div>

        {/* The God Mode Button */}
        <button
          onClick={triggerSimulation}
          disabled={isSimulating || loading}
          className={`w-full flex items-center justify-center gap-2 py-4 font-bold transition-all border-b-2 border-slate-900 ${
            isSimulating 
              ? "bg-slate-700 text-slate-400 cursor-not-allowed" 
              : "bg-amber-600 hover:bg-amber-500 text-white active:bg-amber-700"
          }`}
        >
          {isSimulating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              CALCULATING ECONOMIC SHIFTS...
            </>
          ) : (
            <>
              <Play className="w-5 h-5 fill-current" />
              ADVANCE SIMULATION (1 MONTH)
            </>
          )}
        </button>

        {/* Content Area */}
        <div className="p-8">
          {loading && !isSimulating ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Loader2 className="w-12 h-12 animate-spin mb-4 text-amber-500" />
              <p>Scanning Economy State...</p>
            </div>
          ) : error ? (
            <div className="bg-red-900/20 border border-red-500/50 p-6 rounded text-red-200 text-center">
              <p className="font-bold mb-2">⚠️ SYSTEM ERROR</p>
              <p className="text-sm opacity-80">{error}</p>
              <button
                onClick={fetchQuest}
                className="mt-4 text-xs underline hover:text-white"
              >
                Retry Connection
              </button>
            </div>
          ) : quest ? (
            <div className="space-y-6">
              {/* Quest Title */}
              <div className="text-center pb-6 border-b border-slate-700">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1 block">
                  Active Directive
                </span>
                <h2 className="text-3xl font-bold text-white mb-2 leading-tight">{quest.title}</h2>
                <span className="inline-block px-3 py-1 bg-amber-500/10 text-amber-400 text-xs rounded-full border border-amber-500/20">
                  {quest.type} Protocol
                </span>
              </div>

              {/* Flavor Text */}
              <div className="flex gap-4 bg-slate-900/50 p-4 rounded-lg border border-slate-700/50 italic text-slate-400 leading-relaxed">
                <Scroll className="w-6 h-6 flex-shrink-0 text-slate-600" />
                <p>"{quest.flavor_text}"</p>
              </div>

              {/* Objective & Reward */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-700/30 p-4 rounded-lg border border-slate-600/30">
                  <div className="flex items-center gap-2 mb-2 text-blue-400 font-bold uppercase text-xs tracking-tighter">
                    <Coins className="w-4 h-4" />
                    <h3>Objective</h3>
                  </div>
                  <p className="text-sm text-slate-300 leading-snug">{quest.objective}</p>
                </div>

                <div className="bg-slate-700/30 p-4 rounded-lg border border-slate-600/30">
                  <div className="flex items-center gap-2 mb-2 text-emerald-400 font-bold uppercase text-xs tracking-tighter">
                    <Gift className="w-4 h-4" />
                    <h3>Reward</h3>
                  </div>
                  <p className="text-sm text-slate-300 leading-snug">{quest.reward}</p>
                </div>
              </div>

              <div className="text-center text-[10px] text-slate-600 pt-4 uppercase tracking-[0.2em]">
                Registry ID: {quest._id} • Cycle: {quest.generated_at}
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Footer Decoration */}
      <div className="fixed bottom-4 text-[10px] text-slate-700 uppercase tracking-widest">
        Genesis Core v1.0 // Authored by AI Engineer
      </div>
    </div>
  );
}

export default App;