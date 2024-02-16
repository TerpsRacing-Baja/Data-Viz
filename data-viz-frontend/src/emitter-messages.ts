// Mostly for documentation purposes
export const PLAYBACK_UPDATE = "playback-update";

// This specifies the types of events we emit, note the optional flag b/c there could be one of several type
export type Events = {
  "playback-update"?: { lat: number; lon: number; reversing: boolean };
};
