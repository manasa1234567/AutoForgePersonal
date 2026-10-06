import React from "react";
import { Paper, Typography, List, ListItem, ListItemText } from "@mui/material";

interface Program {
  id: number;
  title: string;
  description?: string;
  active: boolean;
}

interface Props {
  programs: Program[];
}

const AssignedProgramsWidget: React.FC<Props> = ({ programs }) => {
  return (
    <Paper sx={{ p: 2 }} elevation={3} aria-label="Assigned Training Programs">
      <Typography variant="h6" gutterBottom>
        Assigned Training Programs
      </Typography>
      {programs.length === 0 ? (
        <Typography>No assigned programs.</Typography>
      ) : (
        <List dense>
          {programs.map((program) => (
            <ListItem key={program.id}>
              <ListItemText
                primary={program.title}
                secondary={program.description ?? "No description"}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default AssignedProgramsWidget;
