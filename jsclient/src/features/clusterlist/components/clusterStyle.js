import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";

export default makeStyles((theme: Theme) =>
  createStyles({
    summary: {
      padding: 0,
      paddingRight: 15,
      margin: 0,
      '& .MuiExpansionPanelSummary-content': {
        flexDirection: "column",
        padding: "6px 10px",
        margin: 0,

      },
    },
    link: {
      verticalAlign: "middle",
      marginBottom: 4,
      '& a': {
        lineHeight: 1,
        whiteSpace: "nowrap",
        overflow: "hidden",
      },
      '& img': {
        position: "relative",
        top: 4,
        margin: "0 6px 0 1px",
        maxHeight: 18,
        height: 18,
        maxWidth: 18,
        width: 18,
      },

    },
    mainTitle: {
      paddingLeft: 5,
      display: "inline",
      verticalAlign: "middle",
      whiteSpace: "nowrap",
      overflow: "hidden",
    },
    titleAction: {
      padding: 0,
      margin: 0,
    },
    content: {
      display: "block",
      maxWidth: "100%",
    },
  })
);
