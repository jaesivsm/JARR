import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";

import { feedListWidth } from "../../const";

export default makeStyles((theme: Theme) =>
  createStyles({
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
      [theme.breakpoints.down("sm")]: {
        paddingLeft: 10,
        paddingRight: 24
      }
    },
    catItemAll: {
        marginLeft: 25
    },
    feedItem: {
      lineHeight: 1,
      overflow: "hidden",
      paddingLeft: "32px !important",
      whiteSpace: "nowrap",
      [theme.breakpoints.down("sm")]: {
        paddingRight: 24,
        paddingLeft: "18px !important",
      }
    },
    feedItemText: {
      marginRight: 10,
      "& span" : {
          overflow: "hidden",
          maxWidth: "calc(100% - 25px)",
      }
    },
    feedBadge: {
      opacity: 0.6,
      right: 2
    },
    feed: {
      paddingTop: 2,
      paddingBottom: 2,
    },
    welcome: {
      '& .MuiAlert-icon': {
        display: "none",
      },
      '& .MuiAlert-message': {
        padding: 0,
      },
      '& svg': {
        height: 20,
        width: 20,
      },
      '& .MuiButtonBase-root': {
        height: 20,
        width: 20,
        padding: 0,
      },
    },
  }),
);
