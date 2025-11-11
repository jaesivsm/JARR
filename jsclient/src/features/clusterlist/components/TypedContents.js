import React, { useRef, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useNavigate, useLocation } from "react-router-dom";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Slider from "@mui/material/Slider";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import Forward10OutlinedIcon from "@mui/icons-material/Forward10Outlined";
import Replay10OutlinedIcon from "@mui/icons-material/Replay10Outlined";
import Forward5OutlinedIcon from "@mui/icons-material/Forward5Outlined";
import Replay5OutlinedIcon from "@mui/icons-material/Replay5Outlined";

import useStyles from "./style";

export const articleTypes = ["image", "audio", "video"];

function MediaPlayer({ type, article, feedTitle, feedIconUrl, onEnded, autoplay }) {
  const mediaRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const hasLoadedProgressRef = useRef(false);
  const urlUpdateIntervalRef = useRef(null);

  // Update URL with current playback position
  const updateUrlPosition = (position) => {
    const searchParams = new URLSearchParams(window.location.search);
    if (position > 5) {
      searchParams.set('t', Math.floor(position));
      const newSearch = searchParams.toString();
      const newUrl = `${window.location.pathname}?${newSearch}`;
      navigate(newUrl, { replace: true });
    } else {
      searchParams.delete('t');
      const newSearch = searchParams.toString();
      const newUrl = `${window.location.pathname}${newSearch ? '?' + newSearch : ''}`;
      navigate(newUrl, { replace: true });
    }
  };

  useEffect(() => {
    const media = mediaRef.current;
    if (!media) return undefined;

    // Reset progress load flag for new media
    hasLoadedProgressRef.current = false;

    // Load start position from URL parameter only
    // Only runs once when metadata first loads to avoid seeking during playback
    const loadProgress = () => {
      // Guard: only load progress once per video to avoid seeks during playback
      if (hasLoadedProgressRef.current) {
        return;
      }
      hasLoadedProgressRef.current = true;

      try {
        // Check URL parameter for start time
        const searchParams = new URLSearchParams(location.search);
        const urlTime = searchParams.get('t');
        if (urlTime && !isNaN(urlTime)) {
          const position = parseInt(urlTime, 10);
          if (position > 0) {
            media.currentTime = position;
          }
        }
        // Otherwise start from beginning (default behavior)
      } catch (e) {
        console.error("Failed to load media start position:", e);
      }
    };

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

    const handleTimeUpdate = () => {
      setCurrentTime(media.currentTime);
    };
    const handleDurationChange = () => setDuration(media.duration);
    const handleLoadedMetadata = () => {
      loadProgress();
    };
    const handlePlay = () => {
      setIsPlaying(true);
      updateMediaSession();

      // Clear any existing interval
      if (urlUpdateIntervalRef.current) {
        clearInterval(urlUpdateIntervalRef.current);
      }

      // Update URL immediately
      updateUrlPosition(media.currentTime);

      // Set up interval to update URL every 10 seconds
      urlUpdateIntervalRef.current = setInterval(() => {
        if (media && !media.paused && !media.ended) {
          updateUrlPosition(media.currentTime);
        }
      }, 10000);
    };
    const handlePause = () => {
      setIsPlaying(false);

      // Clear interval
      if (urlUpdateIntervalRef.current) {
        clearInterval(urlUpdateIntervalRef.current);
        urlUpdateIntervalRef.current = null;
      }

      // Update URL with final position
      updateUrlPosition(media.currentTime);
    };
    const handleEnded = () => {
      setIsPlaying(false);

      // Clear interval
      if (urlUpdateIntervalRef.current) {
        clearInterval(urlUpdateIntervalRef.current);
        urlUpdateIntervalRef.current = null;
      }

      // Clear URL parameter when media ends
      try {
        const searchParams = new URLSearchParams(location.search);
        searchParams.delete('t');
        const newSearch = searchParams.toString();
        const newUrl = `${location.pathname}${newSearch ? '?' + newSearch : ''}`;
        navigate(newUrl, { replace: true });
      } catch (e) {
        console.error("Failed to clear URL parameter:", e);
      }

      // Call the onEnded callback if provided (for autoplay chain)
      if (onEnded) {
        onEnded();
      }
    };

    media.addEventListener("loadedmetadata", handleLoadedMetadata);
    media.addEventListener("timeupdate", handleTimeUpdate);
    media.addEventListener("durationchange", handleDurationChange);
    media.addEventListener("play", handlePlay);
    media.addEventListener("pause", handlePause);
    media.addEventListener("ended", handleEnded);

    return () => {
      media.removeEventListener("loadedmetadata", handleLoadedMetadata);
      media.removeEventListener("timeupdate", handleTimeUpdate);
      media.removeEventListener("durationchange", handleDurationChange);
      media.removeEventListener("play", handlePlay);
      media.removeEventListener("pause", handlePause);
      media.removeEventListener("ended", handleEnded);

      // Clear URL update interval
      if (urlUpdateIntervalRef.current) {
        clearInterval(urlUpdateIntervalRef.current);
        urlUpdateIntervalRef.current = null;
      }

      // Clear media session on unmount
      if ("mediaSession" in navigator) {
        navigator.mediaSession.metadata = null;
        navigator.mediaSession.setActionHandler("play", null);
        navigator.mediaSession.setActionHandler("pause", null);
        navigator.mediaSession.setActionHandler("seekbackward", null);
        navigator.mediaSession.setActionHandler("seekforward", null);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    // Note: navigate and updateUrlPosition are intentionally omitted to prevent re-initialization
    // location.search is intentionally omitted to prevent re-seeking when URL updates with ?t= parameter
    // The hasLoadedProgressRef guard ensures loadProgress only runs once per video
  }, [article.title, feedTitle, feedIconUrl, article.id, article.link, onEnded]);

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
      const newTime = mediaRef.current.currentTime;
      setCurrentTime(newTime);

      // Update URL immediately
      updateUrlPosition(newTime);
    }
  };

  const handleTimeChange = (event, newValue) => {
    if (mediaRef.current) {
      mediaRef.current.currentTime = newValue;
      setCurrentTime(newValue);
      updateUrlPosition(newValue);
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

  const handlePlaybackRateChange = (event, newValue) => {
    if (mediaRef.current) {
      mediaRef.current.playbackRate = newValue;
      setPlaybackRate(newValue);
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
        autoPlay={autoplay}
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

        <Box sx={{
          display: "flex",
          gap: 0.5,
          justifyContent: "center",
          alignItems: "center",
          flexWrap: "wrap",
          width: "100%"
        }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <IconButton
              size="medium"
              onClick={() => skipTime(-10)}
            >
              <Replay10OutlinedIcon />
            </IconButton>
            <IconButton
              size="medium"
              onClick={() => skipTime(-5)}
            >
              <Replay5OutlinedIcon />
            </IconButton>
            <IconButton
              onClick={togglePlayPause}
              color="primary"
              size="medium"
            >
              {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
            </IconButton>
            <IconButton
              size="medium"
              onClick={() => skipTime(5)}
            >
              <Forward5OutlinedIcon />
            </IconButton>
            <IconButton
              size="medium"
              onClick={() => skipTime(10)}
            >
              <Forward10OutlinedIcon />
            </IconButton>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <IconButton
              onClick={toggleMute}
              size="medium"
            >
              {isMuted ? <VolumeOffIcon /> : <VolumeUpIcon />}
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
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <Typography variant="caption" sx={{ minWidth: "45px", textAlign: "right" }}>
              {playbackRate}x
            </Typography>
            <Slider
              size="small"
              value={playbackRate}
              min={0.75}
              max={2}
              step={0.25}
              marks={[
                { value: 0.75, label: '0.75' },
                { value: 1, label: '1' },
                { value: 1.25, label: '1.25' },
                { value: 1.5, label: '1.5' },
                { value: 1.75, label: '1.75' },
                { value: 2, label: '2' }
              ]}
              onChange={handlePlaybackRateChange}
              sx={{ width: "150px" }}
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
  onEnded: PropTypes.func,
  autoplay: PropTypes.bool,
};

export function TypedContents({ type, articles, hidden, feedTitle, feedIconUrl, onMediaEnded, autoplay }) {
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
          media = <MediaPlayer key={`${type}-${article.id}`} type={type} article={article} feedTitle={feedTitle} feedIconUrl={feedIconUrl} onEnded={onMediaEnded} autoplay={autoplay} />;
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
  onMediaEnded: PropTypes.func,
  autoplay: PropTypes.bool,
};
