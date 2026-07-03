import React from "react";
import {
  AbsoluteFill,
  Sequence,
  Img,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export type HookDemoProps = {
  hookText: string;
  hookSrc: string; // filename in public/ (image or video); "" = solid accent bg
  hookIsVideo: boolean;
  demoSrc: string; // filename in public/ (video)
  demoCaption: string;
  brand: string;
  accentColor: string;
  hookSeconds: number;
  demoSeconds: number;
};

export const hookDemoDefaults: HookDemoProps = {
  hookText: "your closet before vs after",
  hookSrc: "",
  hookIsVideo: false,
  demoSrc: "demo.mp4",
  demoCaption: "",
  brand: "",
  accentColor: "#111111",
  hookSeconds: 3,
  demoSeconds: 8,
};

const SAFE_X = 0.085; // matches caption_composite side margin
const BOTTOM_BAND = 0.1; // platform UI

const HookText: React.FC<{ text: string; accent: string }> = ({ text, accent }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  // pop-in
  const pop = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 12 });
  const scale = interpolate(pop, [0, 1], [0.9, 1]);
  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        padding: `0 ${width * SAFE_X}px ${height * (BOTTOM_BAND + 0.06)}px`,
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          background: "rgba(0,0,0,0.42)",
          color: "#fff",
          fontFamily: "Arial, Helvetica, sans-serif",
          fontWeight: 800,
          fontSize: width * 0.075,
          lineHeight: 1.15,
          textAlign: "center",
          padding: `${width * 0.03}px ${width * 0.04}px`,
          borderRadius: width * 0.03,
          textShadow: "0 2px 8px rgba(0,0,0,0.5)",
          borderLeft: `${width * 0.012}px solid ${accent}`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

export const HookDemo: React.FC<HookDemoProps> = (props) => {
  const { fps } = useVideoConfig();
  const hookFrames = Math.round(props.hookSeconds * fps);
  const demoFrames = Math.round(props.demoSeconds * fps);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* HOOK ~3s */}
      <Sequence durationInFrames={hookFrames} name="hook">
        <AbsoluteFill style={{ backgroundColor: props.accentColor }}>
          {props.hookSrc ? (
            props.hookIsVideo ? (
              <OffthreadVideo src={staticFile(props.hookSrc)} muted />
            ) : (
              <Img src={staticFile(props.hookSrc)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            )
          ) : null}
        </AbsoluteFill>
        <HookText text={props.hookText} accent={props.accentColor} />
      </Sequence>

      {/* DEMO */}
      <Sequence from={hookFrames} durationInFrames={demoFrames} name="demo">
        <AbsoluteFill style={{ backgroundColor: "#000" }}>
          <OffthreadVideo src={staticFile(props.demoSrc)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
        {props.demoCaption || props.brand ? (
          <DemoCaption caption={props.demoCaption} brand={props.brand} accent={props.accentColor} />
        ) : null}
      </Sequence>
    </AbsoluteFill>
  );
};

const DemoCaption: React.FC<{ caption: string; brand: string; accent: string }> = ({ caption, brand, accent }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const appear = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 10 });
  const y = interpolate(appear, [0, 1], [30, 0]);
  const text = caption || (brand ? `i used ${brand}` : "");
  return (
    <AbsoluteFill
      style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: height * 0.14 }}
    >
      <div
        style={{
          transform: `translateY(${y}px)`,
          opacity: appear,
          background: "rgba(0,0,0,0.5)",
          color: "#fff",
          fontFamily: "Arial, Helvetica, sans-serif",
          fontWeight: 700,
          fontSize: width * 0.055,
          padding: `${width * 0.02}px ${width * 0.035}px`,
          borderRadius: width * 0.03,
          borderBottom: `${width * 0.008}px solid ${accent}`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
