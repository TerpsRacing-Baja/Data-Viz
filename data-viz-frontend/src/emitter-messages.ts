// Mostly for documentation purposes
export const PLAYBACK_UPDATE = "playback-update";
export const CAR_SPEED = "car-speeds";

export const SESSION_RESET = "session-reset";

export const GPS_DATA = "gps-data";
export const CSV_FILE = "csv-file"
export const ROTATION = "rotation";
export const GPS_POINT = "gps-point";
export const PLOT_POINT = "plot-point";

export const RPM_DATA = "rpm-data";

export const ACCELERATION_DATA = "acceleration-data"; 

// This specifies the types of events we emit, note the optional flag b/c there could be one of several type
export type Events = {
  "playback-update"?: { index: number };
  "gps-data"?: { coords: [number, number][] };
  "csv-file"?: {file_name: string};
  "car-speeds"?: { velocity: number };
  "session-reset"?: {};
  "rotation"?: {pitch: number, yaw: number, roll: number};
  "gps-point"?: {point: [number, number]};
  "rpm-data"?: {tick: number, rpm1: number, rpm2: number};
  "plot-point"?: {xPoint: number, yPoint: number};
  "acceleration-data"?: {ax: number, ay: number, az: number};
};
