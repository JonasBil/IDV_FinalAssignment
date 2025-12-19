import { writable } from 'svelte/store';

const MAX_SELECTED = 2;

function createSelectedCities() {
  const { subscribe, set, update } = writable([]);

  return {
    subscribe,

    set,

    clear() {
      set([]);
    },

    toggle(cityKey) {
      if (!cityKey) return;

      update((current) => {
        const existingIndex = current.indexOf(cityKey);
        if (existingIndex !== -1) {
          return current.filter((c) => c !== cityKey);
        }

        if (current.length < MAX_SELECTED) {
          return [...current, cityKey];
        }

        // If already at max, replace the oldest selection.
        return [current[1], cityKey];
      });
    }
  };
}

export const selectedCities = createSelectedCities();
