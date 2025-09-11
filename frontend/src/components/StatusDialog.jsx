import { useState, useContext } from "react";
import { createPortal } from 'react-dom';
import { useSubmit } from "react-router-dom";

import { UserContext } from "../store/user-context";
import { TasksContext } from "../store/tasks-context";
import { toast } from 'react-toastify';
import Button from "./ui/Button";
import Dialog from "./ui/Dialog";
import Label from "./ui/Label";
import Textarea from "./ui/TextArea";
import Select from "./ui/Select"

export default function StatusDialog({ open, onOpenChange, task }) {
  const [taskLog, setTaskLog] = useState({
    status: "",
    comment: "",
  });
  const { user } = useContext(UserContext);
  const {selectedTask, elapsedTime, setElapsedTime, logId, setTimerStatus, fetchUserTask} = useContext(TasksContext)

  const submit = useSubmit();

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!taskLog.status) {
      toast.error("Please select a status before submitting.");
      return;
    }
    if (taskLog.comment.trim().length < 10) {
      toast.error("Comment must be at least 10 characters long.");
      return;
    }


    const formData = new FormData();
    formData.append("log_id", logId)
    formData.append("userId", user?.user_id);
    formData.append("taskId", selectedTask?.id);
    formData.append("status", taskLog.status);
    formData.append("comment", taskLog.comment);
    formData.append("duration", elapsedTime);
    formData.append("guid", user?.guid);

    submit(formData, { method: "post" });
    setTimerStatus("idle");
    toast.success(`${task?.name} has been marked as ${taskLog.status}.`);
    setTaskLog({ status: "", comment: "" });
    onOpenChange(false);
    setElapsedTime(0);
    if (user?.ace_user_id) {
      // refresh task list to reflect status change
      fetchUserTask(user.ace_user_id);
    }
  };

  const statusOptions = [
    { value: "completed", label: "Completed" },
    { value: "in progress", label: "In progress" },
  ];

  return createPortal(
    <Dialog open={open} onOpenChange={onOpenChange}>
      <form onSubmit={handleSubmit} className="p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Complete Task</h2>
        </div>
        <div className="space-y-4 py-2">
          {task && (
            <div className="p-3 bg-gray-100 rounded-lg">
              <div className="font-medium">{task.name}</div>
              <div className="text-sm text-gray-500">
                {task.project_name} • {task.supervisor_name}
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="status">Status *</Label>
            <Select
              value={taskLog.status}
              onChange={(value) => setTaskLog(prev => ({ ...prev, status: value }))}
              options={statusOptions}
              name="status"
              id="status"
              required
              placeholder="Select completion status"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="comment">Comments</Label>
            <Textarea
              id="comment"
              name="comment"
              value={taskLog.comment}
              onChange={e => setTaskLog(prev => ({ ...prev, comment: e.target.value }))}
              placeholder="Add any comments about the completed task..."
              rows={4}
            />
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-6">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            type="button"
          >
            Cancel
          </Button>
          <Button type="submit">
            Submit
          </Button>
        </div>
      </form>
    </Dialog>, document.getElementById('modal-root')
  );
}
