export interface Clock {
  epochSeconds(): number;
}

export const systemClock: Clock = {
  epochSeconds: () => Math.floor(Date.now() / 1000)
};
