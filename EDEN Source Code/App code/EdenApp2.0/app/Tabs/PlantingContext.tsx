// Tabs/PlantingContext.tsx
import { createContext } from 'react';

type PlantingDataType = {
  [date: string]: {
    plantName: string;
    podNumber: number;
    npk?: { n: number; p: number; k: number };
  }[];
};

type PlantingContextType = {
  plantingData: PlantingDataType;
  setPlantingData: (data: PlantingDataType) => void;
};

export const PlantingContext = createContext<PlantingContextType | null>(null);
