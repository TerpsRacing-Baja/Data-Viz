// Mostly for documentation purposes
export const CAR_STATE = "car-state";

// This specifies the types of events we emit, note the optional flag b/c there could be one of several type
export type Events = {
  "car-state"?: { lat: number; lon: number };
};
