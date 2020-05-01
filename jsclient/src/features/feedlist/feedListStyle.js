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
    catItemAll: {
        marginLeft: 25
    },
    feedItem: {
      lineHeight: 1,
      overflow: "hidden",
      paddingLeft: "32px !important",
      whiteSpace: "nowrap"
    },
    feedItemText: {
      marginRight: 10,
      "& span" : {
          overflow: "hidden",
          maxWidth: 175,
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
  }),
);
