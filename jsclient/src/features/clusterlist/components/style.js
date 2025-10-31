import { makeStyles } from '@mui/styles';
import { feedListWidth, editPanelWidth, appBarHeight } from "../../../const";

export default makeStyles((theme) => ({
  tabs: {
    maxWidth: "100%",
  },
  article: {
    "& h6": {
      padding: "8px 0",
    },
    "& > p": {
      overflowX: "hidden",
      "& span": {
        paddingRight: 30,
        fontStyle: "bold",
      },
      "& > a": {
        overflowX: "hidden",
        whiteSpace: "nowrap",
        maxWidth: "80%",
        textDecoration: "none",
        "&:hover": {
          textDecoration: "underline"
        }
      }
    },
    "& img": {
      maxWidth: "100%",
      height: "auto"
    },
    "& audio": {
      width: "100%"
    },
    "& video": {
      width: "100%",
      height: "auto"
    }
  },
  articleInner: {
    padding: "16px 0",
    "& iframe": {
      width: "100%"
    },
    "& p a": {
      overflowX: "visible",
      whiteSpace: "normal",
      textDecoration: "none",
      "&:hover": {
        textDecoration: "underline"
      }
    },
    "& a": {
      textDecoration: "none",
      "&:hover": {
        textDecoration: "underline"
      }
    }
  },
  summary: {
    padding: "5px",
    margin: 0,
    "& .MuiAccordionSummary-content": {
      flexDirection: "column",
      padding: 0,
      margin: 2,
      maxWidth: "100%",
      overflow: "hidden",
      whiteSpace: "nowrap",
    },
    "& .MuiAccordionSummary-expandIcon": {
      padding: 6,
    },
  },
  link: {
    verticalAlign: "middle",
    display: "flex",
    paddingBottom: 2,
    justifyContent: "space-between",
    "& a": {
      lineHeight: 1.3,
      whiteSpace: "nowrap",
      overflow: "hidden",
      position: "relative",
      textDecoration: "none",
      fontFamily: "Roboto,Helvetica,Arial,sans-serif",
      fontSize: "14px",
      "&:hover": {
        textDecoration: "underline"
      }
    },
    "& img": {
      position: "relative",
      top: 4,
      margin: "0 3px 0 0",
      maxHeight: 16,
      height: 16,
      maxWidth: 16,
      width: 16,
    },
  },
  mainTitle: {
    fontSize: 14,
    paddingLeft: "2px",
    display: "inline",
    verticalAlign: "bottom",
    maxWidth: "100%",
  },
  mainTitleExpanded: {
     whiteSpace: "normal",
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
    paddingTop: `calc(${appBarHeight}px + ${theme.spacing(2)})`,
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: -feedListWidth,
    marginRight: -editPanelWidth,
    maxWidth: "100%",
    [theme.breakpoints.down("sm")]: {
      paddingLeft: 5,
      paddingRight: 5,
      marginLeft: 0,
    }
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
    top: 3,
    color: theme.palette.text.secondary,
    opacity: .9,
  },
  clusterList: {
    display: "block",
    width: "45%",
  },
  clusterListInner: {
    maxHeight: `calc(100vh - (${appBarHeight}px + 32px))`,
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
      height: 18,
      width: 18 ,
    }
  },
  clusterListCardActionBtn: {
    padding: "5px"
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
    maxHeight: `calc(100vh - (${appBarHeight}px + 32px))`,
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
  },
  videoContainer: {
    verticalAlign: "middle",
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    marginTop: theme.spacing(2),
    overflow: "hidden",
    "& iframe": {
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
    },
    "& object": {
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
    },
    "& embed": {
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
    },
  },
}));
