import { createContext, useContext, useState } from "react";

const RouletteContext = createContext();

export function RouletteProvider({ children }) {
  const [history, setHistory] = useState([]);
  const [neighbors, setNeighbors] = useState([]);
  const [physicalZones, setPhysicalZones] = useState([]);

  const addSpin = (number) => {
    setHistory((prev) => [...prev, number]);
    // atualizar neighbors e physicalZones conforme regras da roleta
  };

  return (
    <RouletteContext.Provider
      value={{ history, neighbors, physicalZones, addSpin }}
    >
      {children}
    </RouletteContext.Provider>
  );
}

export const useRoulette = () => useContext(RouletteContext);
