// Mostly for documentation purposes
export const PLAYBACK_UPDATE = "playback-update";
export const CAR_SPEED = "car-speeds";


export const GPS_DATA = "gps-data";
export const CSV_FILE = "csv-file"

// This specifies the types of events we emit, note the optional flag b/c there could be one of several type
export type Events = {
  "playback-update"?: { index: number };
  "gps-data"?: { coords: [number, number][] };
  "csv-file"?: {file_name: string};
  "car-speeds"?: { velocity: number };
};
