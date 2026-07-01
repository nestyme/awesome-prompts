import React from "react";
import { Composition } from "remotion";
import { HookDemo, hookDemoDefaults } from "./HookDemo";

const FPS = 30;

// One composition: a hook segment followed by an app-demo segment. Total length
// is derived from the two segment durations passed in props (calculateMetadata),
// so the render is always exactly hook + demo long.
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="HookDemo"
      component={HookDemo}
      durationInFrames={FPS * 11}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={hookDemoDefaults}
      calculateMetadata={({ props }) => {
        const total = (props.hookSeconds + props.demoSeconds) * FPS;
        return { durationInFrames: Math.max(FPS, Math.round(total)), fps: FPS };
      }}
    />
  );
};
