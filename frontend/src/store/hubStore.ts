import { create } from 'zustand';

interface HubStore {
  selectedHubId: number | null;
  setSelectedHub: (hubId: number | null) => void;
}

const useHubStore = create<HubStore>((set: any) => ({
  selectedHubId: null,
  setSelectedHub: (hubId: number | null) => set({ selectedHubId: hubId }),
}));

export default useHubStore;
