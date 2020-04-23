import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";
import { editPanelWidth } from "../../const";

export default makeStyles((theme: Theme) =>
  createStyles({
    editPanel: {
      width: editPanelWidth,
      flexShrink: 0,
    },
    editPanelPaper: {
      width: editPanelWidth,
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
      padding: '20px 8px',
    },
    editPanelInput: {
      marginBottom : 30
    },
    editPanelSlide: {
      marginLeft : 15,
      marginRight: 15,
      marginBottom: 20      
    },
    editPanelSubmit: {
      marginTop: 20
    }
  }),
);
