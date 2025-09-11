import { useContext, useState } from "react";
import TimerControls from "../components/TimerControls";
import TaskList from "../components/TaskList";
import StatusDialog from "../components/StatusDialog";
import { TasksContext } from "../store/tasks-context";
import { stopTime } from "../services/api";

export default function TasksPage() {
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);

  const { selectedTask } = useContext(TasksContext);

  const handleStatusChange = (status) => {
    if (status === "completed") {
      setStatusDialogOpen(true);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex-1 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-2">Task Management</h2>
            <p className="text-muted-foreground">
              Select a task and manage your time efficiently
            </p>
          </div>

          <TimerControls
            onStatusChange={handleStatusChange}
          />

          <div className="mb-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Available Tasks</h2>
              {selectedTask && (
                <div className="text-sm text-muted-foreground">
                  Selected: <span className="font-medium text-foreground">{selectedTask.name}</span>
                </div>
              )}
            </div>
          </div>

          <TaskList />

          <StatusDialog
            open={statusDialogOpen}
            onOpenChange={setStatusDialogOpen}
            task={selectedTask}
          />
        </div>
      </div>
    </div>
  );
};



export async function action({ request }) {
  const formData = await request.formData();
  const userid = formData.get("userId");
  const taskid = formData.get("taskId");
  const status = formData.get("status");
  const comment = formData.get("comment");
  const duration = formData.get("duration");
  const log_id = formData.get("log_id")
  const guid = formData.get("guid")

  console.log("Form submitted:", { userid, taskid, guid, status, comment, duration, log_id });
  const response = await stopTime({ userid, taskid,guid, status, comment, duration, log_id });

  return response;
}