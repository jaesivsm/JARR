import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";
import { editPanelWidth } from "../../const";

export default makeStyles((theme: Theme) =>
  createStyles({
    editPanel: {
      width: editPanelWidth,
      flexShrink: 0,
    },
    editPanelPaper: {
      overflow: 'hidden',
      width: editPanelWidth,
    },
    editPanelHeaderSticky: {
      backgroundColor: '#ffffff',
      borderBottom: '1px solid lightgray',
      display: 'block',
      position: 'fixed',
      opacity: 1,
      transition: 'none',
      width: editPanelWidth,
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
      '& fieldset': {
          width: '100%'
      },
      '& .MuiAlert-root': {
        marginBottom: 25
      },
      overflowY: 'auto',
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
      marginLeft : '15px !important',
      marginRight: '15px !important',
      marginBottom: 20      
    },
    editPanelButtons: {
      display: 'flex',
      justifyContent: 'space-between'
    },
    editPanelBtn: {
      marginTop: 20,
      marginBottom: 20
    }
    
  }),
);
