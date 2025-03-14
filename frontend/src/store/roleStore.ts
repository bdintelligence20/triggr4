import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Role = 'guest' | 'user' | 'admin';

interface RoleState {
  role: Role;
  setRole: (role: Role) => void;
}

const useRoleStore = create<RoleState>()(
  persist(
    (set) => ({
      role: 'guest',
      setRole: (role) => set({ role }),
    }),
    {
      name: 'role-storage',
    }
  )
);

export default useRoleStore;
