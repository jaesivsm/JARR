import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";
import { editPanelWidth } from "../../const";
import { jarrColors } from "../../Jarr.theme";

export default makeStyles((theme: Theme) =>
  createStyles({
    editPanel: {
      maxWidth: editPanelWidth,
      [theme.breakpoints.down("sm")]: {
        width: "auto"
      },
      flexShrink: 0,
    },
    editPanelPaper: {
      overflow: "hidden",
      width: editPanelWidth,
      [theme.breakpoints.down("sm")]: {
        width: "100%"
      },
    },
    editPanelHeaderSticky: {
      backgroundColor: "#ffffff",
      borderBottom: "1px solid lightgray",
      display: "block",
      position: "fixed",
      opacity: 1,
      transition: "none",
      width: editPanelWidth,
      [theme.breakpoints.down("sm")]: {
        width: "100%"
      },
      zIndex: 99,
    },
    editPanelHeader: {
      display: "flex",
      alignItems: "center",
      padding: theme.spacing(0, 1),
      // necessary for content to be below app bar
      ...theme.mixins.toolbar,
      justifyContent: "space-between",
    },
    editPanelTitle: {
      padding: theme.spacing(0, 1),
    },
    editPanelForm: {
      "& fieldset": {
          width: "100%"
      },
      "& .MuiAlert-root": {
        marginBottom: 25
      },
      overflowY: "auto",
      marginTop: 70,
      padding: 20,
    },
    editPanelInput: {
      marginBottom : 30
    },
    editPanelSelect: {
      marginBottom: 20
    },
    editPanelSlide: {
      marginLeft : "15px !important",
      marginRight: "15px !important",
      marginBottom: 20
    },
    editPanelButtons: {
      display: "flex",
      justifyContent: "space-between",
      [theme.breakpoints.down("sm")]: {
        flexDirection: "column"
      }
    },
    editPanelBtn: {
      marginTop: 20,
      marginBottom: 20,
      [theme.breakpoints.down("sm")]: {
        marginBottom: 0,
      }
    },
    deletePanelBtn: {
      color: jarrColors.danger.contrastText,
      backgroundColor: jarrColors.danger.main,
      marginTop: 20,
      marginBottom: 20,
      [theme.breakpoints.down("sm")]: {
        marginBottom: 0,
      },
      "&:hover": {
        backgroundColor: jarrColors.danger.hover,
      },
      "& svg": {
        position: "relative",
        left: -8,
      }
    },
    editPanelCluster: {
      marginBottom: 30
    },
    editPanelClusterHeader: {

    },
    editPanelClusterSettings: {
      display: "flex",
      flexDirection: "column"
    },
    editPanelClusterCtrl: {
      justifyContent: "space-between",
      flexDirection: "row",
      [theme.breakpoints.down("sm")]: {
        flexDirection: "column"
      },
    },
    editPanelClusterSelect: {
      marginBottom: 10,
      marginTop: "0 !important",
      "& .MuiSelect-select": {
        width: 150,
        [theme.breakpoints.down("sm")]: {
          width: "100%"
        }
      }
    },
    editPanelClusterLabel: {
      textAlign: "left",
      display: "block",
      paddingTop: 10,
      position: "relative",
      transformOrigin: "top left",
      width: "100%"
    },
    editPanelFilter: {
      display: "table",
      alignItems: "baseline",
      flexDirection: "row",
      marginBottom: 25,
      marginLeft: 16,
      marginRight: 16
    },
    editPanelFilterItem: {
      display: "table-cell",
      "& .MuiInput-root": {
        height: 32,
        justifyContent: "center"
      },
      "& .MuiTextField-root": {
        height: 32,
        justifyContent: "center",
        "& input": {
          padding: 0
        }
      }
    },
    editPanelFilterArrows: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      left: 5,
      position: "absolute"
    },
    editPanelFilterArrow: {
      position: "relative",
      padding: 0,
      "& svg": {
        height: 18,
        width: 18,
      }
    },
    editPanelFilterAddBtn: {
      textAlign: "center",
      width: "100%",
      "& button": {
        minHeight: "unset",
        height: 35,
        width: 35,
      }
    },
    editPanelFilterDelBtn: {
      position: "absolute",
      right: 0,
      padding: 8,
      "& svg": {
        height: 18,
        width: 18
      }
    },
    loadEditPanel: {
      width: "100%",
      textAlign: "center",
      padding: "20px 0",
    },
    showHelpButton: {
      width: 30,
      height: 30,
      margin: "0 auto",
      position: "absolute",
      right: 13,
      top: 44,
    },
  }),
);
