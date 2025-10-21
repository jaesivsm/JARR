import { makeStyles } from '@mui/styles';
import { feedListWidth } from "../../const";

const menuItem = {
    margin: 0,
    padding: "0px 0px 0px 45px",
};

export default makeStyles((theme) => ({
  drawer: {
    width: feedListWidth,
    [theme.breakpoints.down("sm")]: {
      width: "auto"
    },
    flexShrink: 0,
  },
  drawerPaper: {
    width: feedListWidth,
    [theme.breakpoints.down("sm")]: {
      width: "100%"
    },
  },
  drawerHeader: {
    display: "flex",
    alignItems: "center",
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: "space-between",
  },
  category: {
    paddingTop: 2,
    paddingBottom: 2,
  },
  catItem: {
    cursor: "pointer",
    [theme.breakpoints.down("sm")]: {
    },
    ...menuItem,
  },
  catItemAll: {
    ...menuItem,
    paddingLeft: "45px",
  },
  catItemText: {
  },
  feedItem: {
    cursor: "pointer",
    overflow: "hidden",
    whiteSpace: "nowrap",
    position: "relative",
    ...menuItem,
  },
  feedItemText: {
    "& span" : {
      maxWidth: "100%",
      overflow: "hidden",
    }
  },
  feedBadge: {
    opacity: 0.6,
    right: "20px",
    transform: "translateY(-10%)",
  },
  feed: {
    paddingTop: 2,
    paddingBottom: 2,
  },
  welcome: {
    "& .MuiAlert-icon": {
      display: "none",
    },
    "& .MuiAlert-message": {
      padding: 0,
    },
    "& svg": {
      height: 20,
      width: 20,
    },
    "& .MuiButtonBase-root": {
      height: 20,
      width: 20,
      padding: 0,
    },
  },
  foldButton: {
    opacity: 0.7,
    cursor: "pointer",
    transition: "opacity 0.2s, background-color 0.2s",
    borderRadius: "50%",
    marginRight: "15px",
    "&:hover": {
      opacity: 1,
      backgroundColor: "rgba(0, 0, 0, 0.08)",
    },
    "&:active": {
      backgroundColor: "rgba(0, 0, 0, 0.15)",
    },
    [theme.breakpoints.down("sm")]: {
      height: 40,
      width: 40,
    }
  },
  loadFeedList: {
    width: "100%",
    textAlign: "center",
    padding: "20px 0",
  }
}));
