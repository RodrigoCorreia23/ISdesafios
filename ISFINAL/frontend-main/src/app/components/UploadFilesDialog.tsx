import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Typography } from '@mui/material';
import { toast } from 'react-toastify';

const UploadFilesDialog = React.forwardRef((props, ref) => {
  const [open, setOpen] = React.useState(false);
  const [file, setFile] = React.useState<any>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  const handleFileChange = (event: any) => {
    const uploadedFile = event.target.files[0];
    setFile(uploadedFile);
  };

  const handleRemoveFile = () => {
    setFile(null);
  };

  React.useImperativeHandle(ref, () => ({
    handleClickOpen() {
      setOpen(true);
    }
  }));

  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorBody = await response.json();
        console.error("Upload Error:", errorBody);
        toast.error(errorBody.message || "Failed to upload file.");
        return;
      }

      const data = await response.json();
      console.log("Upload Successful:", data);
      toast.success("File uploaded successfully!");
    } catch (error) {
      console.error("Unhandled Error in frontend:", error);
      toast.error("Something went wrong during the upload.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <React.Fragment>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{"Upload File"}</DialogTitle>
        <DialogContent>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              p: 3,
              border: "1px solid #ccc",
              borderRadius: "8px",
            }}
          >
            <Typography variant="h6">Upload .csv File</Typography>
            {file ? (
              <>
                <Typography variant="body1">Selected File: {file.name}</Typography>
                <Button variant="contained" color="error" onClick={handleRemoveFile}>
                  Remove File
                </Button>
              </>
            ) : (
              <Button variant="contained" component="label">
                Select .csv File
                <input type="file" hidden onChange={handleFileChange} accept=".csv" />
              </Button>
            )}
          </Box>

          {loading === true && <p>Loading request...</p>}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button disabled={loading === true} onClick={handleSubmit} autoFocus>
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
});

export default UploadFilesDialog;