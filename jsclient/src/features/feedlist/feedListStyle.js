import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";

import { feedListWidth } from "../../const";

export default makeStyles((theme: Theme) =>
  createStyles({
    drawer: {
      width: feedListWidth,
      flexShrink: 0,
    },
    drawerPaper: {
      width: feedListWidth,
    },
    drawerHeader: {
      display: "flex",
      alignItems: "center",
      padding: theme.spacing(0, 1),
      // necessary for content to be below app bar
      ...theme.mixins.toolbar,
      justifyContent: "space-between",
    },
    feedIcon: {
      maxWidth: 16,
      maxHeight: 16,
      margin: theme.spacing(1),
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
    feetItemText: {
      marginRight: 10,
      "& span" : {
          overflow: "hidden",
          maxWidth: 175,
      }
    },
    feed: {
      paddingTop: 2,
      paddingBottom: 2,
    },
    defaultFeedIcon: {
      margin: 6
    }
  }),
);
