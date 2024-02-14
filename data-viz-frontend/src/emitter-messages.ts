// Mostly for documentation purposes
export const CAR_STATE = "car-state";
export const REVERSE_CAR = "reverse-car";

// This specifies the types of events we emit, note the optional flag b/c there could be one of several type
export type Events = {
  "car-state"?: { lat: number; lon: number };
  "reverse-car"?: { amount: number };
};
