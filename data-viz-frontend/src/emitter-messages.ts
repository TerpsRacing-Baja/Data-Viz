// Mostly for documentation purposes
export const PLAYBACK_UPDATE = "playback-update";
export const CAR_SPEED = "car-speeds";
export const CAR_ROTATION = "car-rot";


export const GPS_DATA = "gps-data";

// This specifies the types of events we emit, note the optional flag b/c there could be one of several type
export type Events = {
  "playback-update"?: { index: number };
  "gps-data"?: { coords: [number, number][] };
  "car-speeds"?: { velocity: number };
  "car-rot"?: { yaw: number, pitch: number, roll: number };
};
