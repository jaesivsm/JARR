import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";
import { feedListWidth, editPanelWidth } from "../../const";

export default makeStyles((theme: Theme) =>
  createStyles({
    content: {
      flexGrow: 1,
      paddingTop: 88,
      padding: theme.spacing(3),
      transition: theme.transitions.create("margin", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      marginLeft: -feedListWidth,
      marginRight: -editPanelWidth,
    },
    contentShift: {
      transition: theme.transitions.create("margin", {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
      marginRight: -editPanelWidth,
    },
  })
);


