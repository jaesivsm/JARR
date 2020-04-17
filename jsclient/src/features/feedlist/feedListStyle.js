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
  }),
);
