import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

function App() {
  const [gameState, setGameState] = useState(null)
  const [menuTab, setMenuTab] = useState('fight') 
  const [gameOverMsg, setGameOverMsg] = useState(null) 
  const [logPosition, setLogPosition] = useState('right')
  const logEndRef = useRef(null)

  const fetchState = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/get_battle_state')
      setGameState(response.data)
      if (response.data.player && response.data.player.hp === 0) setMenuTab('switch')
    } catch (error) {
      console.error("API error", error)
    }
  }

  const startGame = async () => {
    setGameOverMsg(null)
    await axios.post('http://127.0.0.1:8000/start_game')
    fetchState()
    setMenuTab('fight')
  }

  const handleAction = async (actionType, actionIndex) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/execute_turn', { action_type: actionType, index: actionIndex })
      if (response.data.status === "game_over") {
        setGameOverMsg(response.data.winner) 
      } else {
        setGameState(response.data)
        if (response.data.player.hp > 0) setMenuTab('fight')
        else setMenuTab('switch') 
      }
    } catch (error) {
      console.error("Action failed", error)
    }
  }

  useEffect(() => { fetchState() }, [])
  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: "smooth" }) }, [gameState?.log])

  if (!gameState || gameState.status === "waiting") {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-slate-900 text-white">
        <h1 className="text-5xl font-black mb-8 tracking-widest text-yellow-400 drop-shadow-[0_5px_5px_rgba(0,0,0,0.8)]">POKEMON ENGINE</h1>
        <button onClick={startGame} className="px-10 py-4 bg-blue-600 hover:bg-blue-500 rounded-lg text-2xl font-bold transition-all shadow-lg hover:scale-105">
          START BATTLE
        </button>
      </div>
    )
  }

  const isPlayerFainted = gameState.player.hp === 0;
  const isOpponentFainted = gameState.opponent.hp === 0;

  const getSpriteName = (fullName) => {
    if (!fullName) return "substitute";
    const parts = fullName.split('] ');
    let name = parts.length > 1 ? parts[1] : fullName;
    return name.toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  const getStatusBadge = (status) => {
    if (!status || status === "NONE") return null;
    const statusConfig = {
      "PARALYZE": { text: "PAR", color: "bg-yellow-400 text-yellow-900" },
      "POISON": { text: "PSN", color: "bg-purple-500 text-white" },
      "BURN": { text: "BRN", color: "bg-red-500 text-white" },
      "FREEZE": { text: "FRZ", color: "bg-cyan-300 text-cyan-900" },
      "SLEEP": { text: "SLP", color: "bg-slate-400 text-slate-900" }
    };
    const config = statusConfig[status] || { text: status, color: "bg-gray-500 text-white" };
    return <span className={`ml-2 px-1 rounded text-[10px] font-black tracking-wider ${config.color} border border-black/20`}>{config.text}</span>;
  }

  return (
    <div className="h-screen w-screen bg-slate-900 text-white p-2 md:p-4 font-mono flex flex-col overflow-hidden">
      
      {gameOverMsg && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center backdrop-blur-sm">
          <div className="bg-slate-800 border-4 border-yellow-500 rounded-2xl p-10 max-w-lg w-full text-center shadow-2xl animate-bounce">
            <h2 className="text-5xl font-black text-yellow-400 mb-6 tracking-widest">BATTLE OVER</h2>
            <p className="text-2xl text-slate-200 mb-10 font-bold">{gameOverMsg}</p>
            <button onClick={() => { setGameOverMsg(null); setGameState({ status: "waiting" }); }} className="w-full py-4 bg-blue-600 rounded-lg text-xl font-bold">PLAY AGAIN</button>
          </div>
        </div>
      )}

      {/* TOP HEADER */}
      <div className="h-12 flex-shrink-0 w-full flex justify-between items-center px-4 bg-slate-800 rounded-lg border border-slate-700 shadow-md mb-2">
        <span className="text-lg font-bold text-slate-300">Turn: {gameState.turn}</span>
        {gameState.weather !== "CLEAR" && <span className="text-blue-400 font-bold bg-blue-900/30 px-3 py-1 rounded text-sm">Weather: {gameState.weather}</span>}
      </div>

      <div className={`flex-1 flex gap-2 md:gap-4 min-h-0 ${logPosition === 'left' ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* MINIMALIST BATTLEFIELD */}
        <div className="flex-1 relative bg-[url('https://play.pokemonshowdown.com/sprites/gen6bg/hd-indigo.png')] bg-cover bg-center rounded-xl border-2 border-slate-600 shadow-inner overflow-hidden flex flex-col justify-between p-4 md:p-8">
          
          {/* OPPONENT AREA (Top Right) */}
          <div className="absolute top-[10%] right-[2%] md:right-[5%] flex flex-col items-center z-20">
            {/* Minimal HP Pill */}
            <div className="bg-black/60 backdrop-blur-sm px-3 py-1.5 rounded-full flex items-center gap-2 border border-slate-500/50 shadow-lg mb-4">
              <span className="font-bold text-sm tracking-widest flex items-center">
                {gameState.opponent.name} {getStatusBadge(gameState.opponent.status)}
              </span>
              <span className="text-[10px] text-yellow-400 font-black">Lv50</span>
              <div className="w-24 md:w-32 bg-slate-800 h-2 rounded-full overflow-hidden border border-black">
                <div className={`h-full transition-all duration-700 ${isOpponentFainted ? 'bg-red-600' : 'bg-green-500'}`} style={{ width: `${(gameState.opponent.hp / gameState.opponent.max_hp) * 100}%` }}></div>
              </div>
            </div>
            
            {/* Sprite with Sinking Faint Animation */}
            <img 
               src={`/sprites/front/${getSpriteName(gameState.opponent.name)}.gif`} 
               onError={(e) => {e.target.onerror = null; e.target.src = `https://play.pokemonshowdown.com/sprites/gen5ani/${getSpriteName(gameState.opponent.name)}.gif`}}
               className={`scale-150 drop-shadow-[0_10px_10px_rgba(0,0,0,0.5)] transition-all duration-700 ${isOpponentFainted ? 'opacity-0 translate-y-10' : 'opacity-100 translate-y-0'}`} 
               alt="opponent" 
            />
          </div>

          {/* PLAYER AREA (Bottom Left) */}
          <div className="absolute bottom-[15%] left-[2%] md:left-[5%] flex flex-col items-center z-20">
            {/* Sprite with Sinking Faint Animation */}
            <img 
               src={`/sprites/back/${getSpriteName(gameState.player.name)}.gif`} 
               onError={(e) => {e.target.onerror = null; e.target.src = `https://play.pokemonshowdown.com/sprites/gen5ani-back/${getSpriteName(gameState.player.name)}.gif`}}
               className={`scale-[2.0] drop-shadow-[0_10px_10px_rgba(0,0,0,0.5)] transition-all duration-700 mb-6 ${isPlayerFainted ? 'opacity-0 translate-y-10' : 'opacity-100 translate-y-0'}`} 
               alt="player" 
            />
            
            {/* Minimal HP Pill + HP Numbers */}
            <div className="bg-black/60 backdrop-blur-sm px-4 py-2 rounded-full flex flex-col items-end border border-slate-500/50 shadow-lg mt-2">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-bold text-sm tracking-widest flex items-center">
                  {gameState.player.name} {getStatusBadge(gameState.player.status)}
                </span>
                <span className="text-[10px] text-yellow-400 font-black">Lv50</span>
                <div className="w-32 md:w-48 bg-slate-800 h-2.5 rounded-full overflow-hidden border border-black">
                  <div className={`h-full transition-all duration-700 ${isPlayerFainted ? 'bg-red-600' : 'bg-green-500'}`} style={{ width: `${(gameState.player.hp / gameState.player.max_hp) * 100}%` }}></div>
                </div>
              </div>
              <span className="text-xs font-bold text-slate-300 pr-1">{gameState.player.hp} / {gameState.player.max_hp}</span>
            </div>
          </div>
        </div>

        {/* LOG PANEL */}
        <div className="w-64 md:w-80 flex-shrink-0 bg-black/40 backdrop-blur-md border border-slate-700 rounded-xl flex flex-col shadow-xl">
          <div className="h-10 flex justify-between items-center px-4 border-b border-slate-700 bg-black/20">
            <span className="font-bold text-sm text-slate-300 tracking-wider">BATTLE LOG</span>
            <button onClick={() => setLogPosition(prev => prev === 'right' ? 'left' : 'right')} className="text-slate-400 hover:text-white px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded text-xs border border-slate-600">
              {logPosition === 'right' ? '◀ MOVE' : 'MOVE ▶'}
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 text-sm font-mono text-slate-200">
            {gameState.log && gameState.log.length > 0 ? gameState.log.map((line, idx) => (
                <div key={idx} className={`mb-1 ${line.includes('fainted') ? 'text-red-400 font-bold' : line.includes('super effective') ? 'text-yellow-400' : ''}`}>{line}</div>
              )) : <div className="text-slate-500 italic">Waiting for turn...</div>}
            <div ref={logEndRef} />
          </div>
        </div>

      </div>

      {/* BOTTOM CONTROLS */}
      <div className="h-48 md:h-56 flex-shrink-0 mt-2 bg-slate-800 border-2 border-slate-600 rounded-xl flex flex-col overflow-hidden shadow-lg">
        <div className="flex border-b-2 border-slate-700 h-12 flex-shrink-0">
          <button disabled={isPlayerFainted} onClick={() => setMenuTab('fight')} className={`flex-1 font-black transition-all ${isPlayerFainted ? 'bg-slate-900 text-slate-600 opacity-50' : menuTab === 'fight' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}>FIGHT</button>
          <button onClick={() => setMenuTab('switch')} className={`flex-1 font-black transition-all ${menuTab === 'switch' ? 'bg-green-600 text-white' : isPlayerFainted ? 'bg-green-700/50 text-green-300 animate-pulse' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}>POKEMON</button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 md:p-4 bg-slate-900/50">
          {menuTab === 'fight' && !isPlayerFainted && (
            <div className="grid grid-cols-2 gap-2 md:gap-4 h-full">
              {gameState.player.moves.map((move, idx) => (
                <button key={idx} onClick={() => handleAction("move", idx)} disabled={move.pp === 0} className="bg-slate-700 hover:bg-slate-600 disabled:opacity-50 border border-slate-500 rounded-lg flex flex-col justify-center px-4 transition-transform hover:scale-[1.02]">
                  <div className="flex justify-between w-full items-center"><span className="font-bold text-lg">{move.name}</span><span className="text-xs bg-slate-900 px-2 py-1 rounded border border-slate-600 text-slate-300">PP {move.pp}/{move.max_pp}</span></div>
                  <span className="text-xs text-left text-slate-400 mt-1 font-bold tracking-wider">{move.element}</span>
                </button>
              ))}
            </div>
          )}
          {menuTab === 'switch' && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-4 h-full">
              {gameState.player.party.map((poke, idx) => {
                const isDead = poke.hp === 0;
                return (
                  <button key={idx} onClick={() => handleAction("switch", idx)} disabled={isDead || poke.is_active} className={`border p-2 rounded-lg flex flex-col justify-between ${poke.is_active ? 'bg-blue-900/30 border-blue-500 grayscale-[50%]' : isDead ? 'bg-red-900/20 border-red-900 grayscale' : 'bg-slate-700 hover:bg-slate-600 hover:border-green-400'}`}>
                    <div className="flex justify-between items-center w-full"><span className="font-bold text-sm truncate">{poke.name}</span></div>
                    <div className="w-full bg-slate-900 rounded-full h-2 my-1"><div className={`h-2 ${isDead ? 'bg-red-600' : 'bg-green-500'}`} style={{ width: `${(poke.hp / poke.max_hp) * 100}%` }}></div></div>
                    <div className="text-right text-xs text-slate-300 font-mono">{poke.hp}/{poke.max_hp}</div>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App