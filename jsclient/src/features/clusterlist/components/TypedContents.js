import React, { useRef, useState, useEffect } from "react";
import PropTypes from "prop-types";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Slider from "@mui/material/Slider";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";

import useStyles from "./style";

export const articleTypes = ["image", "audio", "video"];

function MediaPlayer({ type, article, feedTitle, feedIconUrl }) {
  const mediaRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    const media = mediaRef.current;
    if (!media) return;

    const updateMediaSession = () => {
      if ("mediaSession" in navigator && article.title) {
        const metadata = {
          title: article.title,
          artist: feedTitle,
          album: "JARR",
        };

        if (feedIconUrl) {
          metadata.artwork = [
            { src: feedIconUrl, sizes: "96x96", type: "image/png" },
            { src: feedIconUrl, sizes: "128x128", type: "image/png" },
            { src: feedIconUrl, sizes: "192x192", type: "image/png" },
            { src: feedIconUrl, sizes: "256x256", type: "image/png" },
            { src: feedIconUrl, sizes: "384x384", type: "image/png" },
            { src: feedIconUrl, sizes: "512x512", type: "image/png" },
          ];
        }

        navigator.mediaSession.metadata = new MediaMetadata(metadata);

        navigator.mediaSession.setActionHandler("play", () => {
          mediaRef.current?.play();
        });
        navigator.mediaSession.setActionHandler("pause", () => {
          mediaRef.current?.pause();
        });
        navigator.mediaSession.setActionHandler("seekbackward", () => {
          if (mediaRef.current) {
            mediaRef.current.currentTime -= 10;
          }
        });
        navigator.mediaSession.setActionHandler("seekforward", () => {
          if (mediaRef.current) {
            mediaRef.current.currentTime += 10;
          }
        });
      }
    };

    const handleTimeUpdate = () => setCurrentTime(media.currentTime);
    const handleDurationChange = () => setDuration(media.duration);
    const handlePlay = () => {
      setIsPlaying(true);
      updateMediaSession();
    };
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => setIsPlaying(false);

    media.addEventListener("timeupdate", handleTimeUpdate);
    media.addEventListener("durationchange", handleDurationChange);
    media.addEventListener("play", handlePlay);
    media.addEventListener("pause", handlePause);
    media.addEventListener("ended", handleEnded);

    return () => {
      media.removeEventListener("timeupdate", handleTimeUpdate);
      media.removeEventListener("durationchange", handleDurationChange);
      media.removeEventListener("play", handlePlay);
      media.removeEventListener("pause", handlePause);
      media.removeEventListener("ended", handleEnded);

      // Clear media session on unmount
      if ("mediaSession" in navigator) {
        navigator.mediaSession.metadata = null;
        navigator.mediaSession.setActionHandler("play", null);
        navigator.mediaSession.setActionHandler("pause", null);
        navigator.mediaSession.setActionHandler("seekbackward", null);
        navigator.mediaSession.setActionHandler("seekforward", null);
      }
    };
  }, [article.title, feedTitle, feedIconUrl]);

  const togglePlayPause = () => {
    if (mediaRef.current) {
      if (isPlaying) {
        mediaRef.current.pause();
      } else {
        mediaRef.current.play();
      }
    }
  };

  const skipTime = (seconds) => {
    if (mediaRef.current) {
      mediaRef.current.currentTime += seconds;
    }
  };

  const handleTimeChange = (event, newValue) => {
    if (mediaRef.current) {
      mediaRef.current.currentTime = newValue;
      setCurrentTime(newValue);
    }
  };

  const handleVolumeChange = (event, newValue) => {
    if (mediaRef.current) {
      mediaRef.current.volume = newValue;
      setVolume(newValue);
      if (newValue > 0 && isMuted) {
        setIsMuted(false);
        mediaRef.current.muted = false;
      }
    }
  };

  const toggleMute = () => {
    if (mediaRef.current) {
      mediaRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatTime = (time) => {
    if (isNaN(time)) return "0:00";
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const MediaElement = type === "audio" ? "audio" : "video";
  const mediaProps = type === "audio" ? {} : { loop: true };

  return (
    <Box>
      {article.title && (
        <Typography variant="h6" key={`title-${article.id}`}>
          {article.title}
        </Typography>
      )}
      <MediaElement
        ref={mediaRef}
        key={`${type}-${article.id}`}
        {...mediaProps}
      >
        <source src={article.link} />
      </MediaElement>

      <Box sx={{ mt: 2 }}>
        {/* Time progression slider */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
          <Typography variant="caption" sx={{ minWidth: "40px" }}>
            {formatTime(currentTime)}
          </Typography>
          <Slider
            size="small"
            value={currentTime}
            max={duration || 100}
            onChange={handleTimeChange}
            sx={{ flex: 1 }}
          />
          <Typography variant="caption" sx={{ minWidth: "40px" }}>
            {formatTime(duration)}
          </Typography>
        </Box>

        {/* All controls in one responsive line */}
        <Box sx={{
          display: "flex",
          gap: 0.5,
          justifyContent: "center",
          alignItems: "center",
          flexWrap: "wrap",
          width: "100%"
        }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => skipTime(-15)}
              sx={{ textTransform: "none", minWidth: "45px", padding: "4px 8px", fontSize: "0.75rem" }}
            >
              -15s
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => skipTime(-5)}
              sx={{ textTransform: "none", minWidth: "40px", padding: "4px 8px", fontSize: "0.75rem" }}
            >
              -5s
            </Button>
            <IconButton
              onClick={togglePlayPause}
              color="primary"
              size="small"
            >
              {isPlaying ? <PauseIcon fontSize="small" /> : <PlayArrowIcon fontSize="small" />}
            </IconButton>
            <Button
              variant="outlined"
              size="small"
              onClick={() => skipTime(5)}
              sx={{ textTransform: "none", minWidth: "40px", padding: "4px 8px", fontSize: "0.75rem" }}
            >
              +5s
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => skipTime(15)}
              sx={{ textTransform: "none", minWidth: "45px", padding: "4px 8px", fontSize: "0.75rem" }}
            >
              +15s
            </Button>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <IconButton
              onClick={toggleMute}
              size="small"
            >
              {isMuted ? <VolumeOffIcon fontSize="small" /> : <VolumeUpIcon fontSize="small" />}
            </IconButton>
            <Slider
              size="small"
              value={isMuted ? 0 : volume}
              max={1}
              step={0.01}
              onChange={handleVolumeChange}
              sx={{ width: "80px" }}
            />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

MediaPlayer.propTypes = {
  type: PropTypes.oneOf(["audio", "video"]).isRequired,
  article: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string,
    link: PropTypes.string.isRequired,
  }).isRequired,
  feedTitle: PropTypes.string,
  feedIconUrl: PropTypes.string,
};

export function TypedContents({ type, articles, hidden, feedTitle, feedIconUrl }) {
  const classes = useStyles();
  if (articles.length === 0) { return ; }
  let processedUrls = [];
  return (
    <div hidden={!!hidden} className={classes.article}>
      {articles.filter(
          (article) => {
            if (processedUrls.includes(article.link)) {
              return false;
            }
            processedUrls.push(article.link);
            return true;
          }).map((article) => {
        let media;
        if (type === "image") {
          media = (<img key={`image-${article.id}`}
                        src={article.link}
                        alt={article.title} title={article.title} />);
        } else if (type === "audio" || type === "video") {
          media = <MediaPlayer key={`${type}-${article.id}`} type={type} article={article} feedTitle={feedTitle} feedIconUrl={feedIconUrl} />;
        }
        return media;
      })}
    </div>);
}

TypedContents.propTypes = {
  type: PropTypes.string.isRequired,
  articles: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string,
    link: PropTypes.string.isRequired,
    "article_type": PropTypes.string.isRequired})),
  hidden: PropTypes.bool.isRequired,
  feedTitle: PropTypes.string,
  feedIconUrl: PropTypes.string,
};
