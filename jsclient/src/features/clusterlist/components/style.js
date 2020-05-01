import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";
import { feedListWidth, editPanelWidth } from "../../../const";

export default makeStyles((theme: Theme) =>
  createStyles({
    tabs: {
      maxWidth: "100%",
    },
    article: {
      overflowX: "hidden",
      "& p": {
        maxWidth: 800,
        "& span": {
          paddingRight: 30,
          fontStyle: "bold",
        },
      },
      "& img": {
        maxWidth: "100%"
      }
    },
    articleInner: {
      padding: "16px 0"
    },
    summary: {
      padding: 0,
      paddingRight: 15,
      margin: 0,
      "& .MuiExpansionPanelSummary-content": {
        flexDirection: "column",
        padding: "6px 0 6px 10px",
        margin: 0,
        maxWidth: "100%",
        overflow: "hidden",
        whiteSpace: "nowrap",
      },
      "& .MuiExpansionPanelSummary-expandIcon": {
        padding: 6,
      },
    },
    link: {
      verticalAlign: "middle",
      display: "flex",
      justifyContent: "space-between",
      "& a": {
        lineHeight: 1.4,
        whiteSpace: "nowrap",
        overflow: "hidden",
        position: "relative",
        top: 3,
        marginBottom: 5
      },
      "& img": {
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
      fontSize: 14,
      paddingLeft: 5,
      display: "inline",
      verticalAlign: "bottom",
      whiteSpace: "nowrap",
      overflow: "hidden",
      maxWidth: "100%",
    },
    mainTitleExpanded: {
      whiteSpace: "break-spaces",
    },
    titleAction: {
      padding: 0,
      margin: 0,
    },
    content: {
      display: "block",
      maxWidth: "100%",
    },
    main: {
      flexGrow: 1,
      paddingTop: 64+ theme.spacing(2),
      transition: theme.transitions.create("margin", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      marginLeft: -feedListWidth,
      marginRight: -editPanelWidth,
      maxWidth: `100%`,
    },
    mainShifted: {
      transition: theme.transitions.create("margin", {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
      maxWidth: `calc(100% - ${feedListWidth}px)`,
    },
    mainSplitted: {
      display: "flex",
      justifyContent: "space-between",
    },
    clusterDate: {
      position: "absolute",
      right: 15,
      fontSize: 12,
      top: 2,
      color: "#5F9EA0",
      opacity: .9,
    },
    clusterList: {
      display: "block",
      width: "45%",
    },
    clusterListInner: {
      maxHeight: "calc(100vh - (64px + 32px))",
      maxWidth: "100%",
      overflowY: "auto",
      overflowX: "hidden",
      padding: "0 16px"
    },
    clusterListShifted: {
      display: "block",
      width: "40%",
    },
    clusterLoadMore: {
      width: "100%",
      textAlign: "center",
      padding: "20px 0",
    },
    clusterListCard: {
      display: "flex",
      justifyContent: "space-between",
      marginBottom: 30
    },
    clusterListCardTitle: {
      display: "flex",
      alignItems: "center",
      paddingLeft: "10px !important",
      "& img": {
        margin: "0 8px 0 0"
      }
    },
    clusterListCardActions: {
      display: "flex",
      "& svg": {
        height: 15,
        width: 15,
      }
    },
    clusterListCardActionBtn: {
      padding: 0
    },
    contentPanel: {
      display: "block",
      width: "55%",
      marginLeft: theme.spacing(2),
      marginRight: theme.spacing(2),
      /* "& *": {
        maxWidth: "97%",
      }, */
    },
    contentPanelInner: {
      maxHeight: "calc(100vh - (64px + 32px))",
      maxWidth: "100%",
      overflowY: "auto",
      overflowX: "hidden",
      padding: "16px",
    },
    contentPanelShifted: {
      display: "block",
      width: "60%",
      overflowY: "auto",
      overflowX: "hidden",
    },
    loadingWrap: {
      height: 50,
      width: "100%",
      textAlign: "center",
    }
  })
);
