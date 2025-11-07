import React, { useEffect, useRef, useMemo } from "react";
import PropTypes from "prop-types";
import { useLocation, useNavigate } from "react-router-dom";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";
import Divider from "@mui/material/Divider";

import useStyles from "./style";

function ProcessedContent({ content, hidden, onMediaEnded, autoplay }) {
  const classes = useStyles();
  const location = useLocation();
  const navigate = useNavigate();
  const playerRef = useRef(null);
  const updateUrlTimerRef = useRef(null);
  const intervalRef = useRef(null);
  const initialStartTimeRef = useRef(null);
  const lastContentLinkRef = useRef(null);

  // Capture initial start time for each new video
  if (content.type === "youtube" && content.link !== lastContentLinkRef.current) {
    lastContentLinkRef.current = content.link;
    const searchParams = new URLSearchParams(location.search);
    const startTime = searchParams.get('t');
    if (startTime && !isNaN(startTime)) {
      initialStartTimeRef.current = startTime;
    } else {
      initialStartTimeRef.current = false; // Mark as checked
    }
  }

  // Build YouTube URL with start time from initial URL only (always call, even if not youtube)
  const youtubeUrl = useMemo(() => {
    if (content.type !== "youtube") return null;

    let url = `https://www.youtube-nocookie.com/embed/${content.link}`;

    // Add URL parameters for YouTube player
    const urlParams = new URLSearchParams();
    if (initialStartTimeRef.current && initialStartTimeRef.current !== false) {
      urlParams.set('start', initialStartTimeRef.current);
    }
    // Enable JS API for progression tracking
    urlParams.set('enablejsapi', '1');
    urlParams.set('origin', window.location.origin);

    const paramsString = urlParams.toString();
    if (paramsString) {
      url += `?${paramsString}`;
    }
    return url;
  }, [content.type, content.link]); // Only re-create if type or video ID changes

  let title, titleDivider, link, comments, linksDivider, body;
  if (content.type === "fetched") {
    if (content.title) {
      title = (<Typography variant="h6">{content.title}</Typography>);
      titleDivider = <Divider />;
    }
    if (content.comments) {
      comments = (
        <p>
          <span>Comments</span>
          <Link color="secondary" target="_blank" href={content.comments}>
            {content.comments}
          </Link>
        </p>
      );
    }
    link = (
      <p>
        <span>Link</span>
        <Link color="secondary" target="_blank" href={content.link}>
          {content.link}
        </Link>
      </p>
    );
    body = (
      <Typography className={classes.articleInner}
          dangerouslySetInnerHTML={{__html: content.content}} />
    );
    linksDivider = <Divider />;
  } else if (content.type === "youtube") {
    body = (
      <Typography className={classes.videoContainer}>
        <iframe key={`jarr-youtube-${content.link}`}
          title="JARR processed Player"
          id={`ytplayer-${content.link}`}
          type="text/html"
          src={youtubeUrl}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
          referrerPolicy="strict-origin-when-cross-origin"
        />
      </Typography>
    );
  }

  // YouTube IFrame API integration for progression tracking
  useEffect(() => {
    if (content.type !== "youtube" || hidden) return undefined;

    // Load YouTube IFrame API
    if (!window.YT) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }

    const initPlayer = () => {
      const iframe = document.getElementById(`ytplayer-${content.link}`);
      if (!iframe || !window.YT || !window.YT.Player) return;

      try {
        playerRef.current = new window.YT.Player(`ytplayer-${content.link}`, {
          events: {
            'onReady': (event) => {
              // Autoplay when ready if autoplay is enabled
              if (autoplay) {
                event.target.playVideo();
              }
            },
            'onStateChange': (event) => {
              // Clear any existing interval
              if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
              }

              // Handle video ended
              if (event.data === window.YT.PlayerState.ENDED) {
                // Clear URL parameter
                const searchParams = new URLSearchParams(window.location.search);
                searchParams.delete('t');
                const newSearch = searchParams.toString();
                const newUrl = `${window.location.pathname}${newSearch ? '?' + newSearch : ''}`;
                navigate(newUrl, { replace: true });

                // Call onMediaEnded callback for autoplay chain
                if (onMediaEnded) {
                  onMediaEnded();
                }
              }

              // Update URL when video is playing
              if (event.data === window.YT.PlayerState.PLAYING) {
                const updateUrl = () => {
                  if (playerRef.current && playerRef.current.getCurrentTime) {
                    const currentTime = Math.floor(playerRef.current.getCurrentTime());
                    if (currentTime > 5) {
                      if (updateUrlTimerRef.current) {
                        clearTimeout(updateUrlTimerRef.current);
                      }
                      updateUrlTimerRef.current = setTimeout(() => {
                        const currentSearchParams = new URLSearchParams(window.location.search);
                        currentSearchParams.set('t', currentTime);
                        const newUrl = `${window.location.pathname}?${currentSearchParams.toString()}`;
                        navigate(newUrl, { replace: true });
                      }, 2000);
                    }
                  }
                };

                // Update URL immediately when starting
                updateUrl();

                // Update URL every 10 seconds while playing
                intervalRef.current = setInterval(() => {
                  if (playerRef.current && playerRef.current.getPlayerState) {
                    if (playerRef.current.getPlayerState() === window.YT.PlayerState.PLAYING) {
                      updateUrl();
                    } else {
                      if (intervalRef.current) {
                        clearInterval(intervalRef.current);
                        intervalRef.current = null;
                      }
                    }
                  }
                }, 10000);
              }
            }
          }
        });
      } catch (e) {
        console.error("Failed to initialize YouTube player:", e);
      }
    };

    // Wait for API to be ready
    if (window.YT && window.YT.Player) {
      initPlayer();
    } else {
      window.onYouTubeIframeAPIReady = initPlayer;
    }

    return () => {
      if (updateUrlTimerRef.current) {
        clearTimeout(updateUrlTimerRef.current);
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      playerRef.current = null;
    };
  }, [content.type, content.link, hidden, navigate, autoplay, onMediaEnded]);
  return (
    <div hidden={hidden} className={classes.article}>
      {title}
      {titleDivider}
      {link}
      {comments}
      {linksDivider}
      {body}
    </div>
  );
}

ProcessedContent.propTypes = {
  content: PropTypes.shape({
    type: PropTypes.string.isRequired,
    link: PropTypes.string.isRequired,
    content: PropTypes.string,
    comments: PropTypes.string
  }),
  hidden: PropTypes.bool.isRequired,
  onMediaEnded: PropTypes.func,
  autoplay: PropTypes.bool,
};

export default ProcessedContent;
