import { useState, useEffect, useContext } from "react";
import { Play, Pause, Square } from "lucide-react";
import { TasksContext } from "../store/tasks-context";
import Button from "./ui/Button"
import { startTime } from "../services/api";
import { UserContext } from "../store/user-context";
import { toast } from "react-toastify";
import { pauseTime } from '../services/api';

export default function TimerControls({ onStatusChange }) {

  const { user } = useContext(UserContext)

  const { selectedTask, elapsedTime, setElapsedTime, setLogId, timerStatus, setTimerStatus , logId} = useContext(TasksContext)

  useEffect(() => {
    let interval;

    if (timerStatus === "running") {
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [timerStatus]);


  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleStart = async () => {
    if (!selectedTask) {
      toast.error("Select task first");
      return;
    }
    const res = await startTime({ user_id: user.user_id, ace_task_id: selectedTask.id })
    console.log(res)
    setLogId(res.log_id)
    setTimerStatus("running");
  };


  const handlePause = async () => {
    if (!selectedTask) {
      toast.error("Select task first");
      return;
    }

    setTimerStatus("paused");

    if (selectedTask && logId) {
      try {
        await pauseTime({ log_id: logId, duration: elapsedTime });
        toast.success("Task paused and saved");
      } catch (error) {
        toast.error("Failed to pause task");
        console.error(error);
      }
    }
  };


  const handleStop = () => {
    if (!selectedTask) {
      toast.error("Select task first");
      return;
    }
    // setTimerStatus("idle");
    onStatusChange("completed");
    if (selectedTask) {
      const taskKey = `elapsedTime-${selectedTask.id}`;
      localStorage.removeItem(taskKey);
    }
  };

  return (
    <div className="bg-white border rounded-lg shadow p-6 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-3xl font-mono tabular-nums">
            {formatTime(elapsedTime)}
          </div>
          {selectedTask && (
            <div className="text-sm text-muted-foreground">
              {selectedTask.name} - {selectedTask.project_name}
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={handleStart}
            disabled={!selectedTask || timerStatus === "running"}
            className={`bg-green-500 hover:bg-green-600 text-white ${(!selectedTask || timerStatus === "running") && "opacity-50"}`}
          >
            <Play size={16} className="mr-2" />
            Start
          </Button>

          <Button
            onClick={handlePause}
            disabled={!selectedTask || timerStatus !== "running"}
            className={`bg-yellow-500 hover:bg-yellow-600 text-white ${(!selectedTask || timerStatus !== "running") && "opacity-50"}`}
          >
            <Pause size={16} className="mr-2" />
            Pause
          </Button>

          <Button
            onClick={handleStop}
            disabled={!selectedTask || timerStatus === "idle"}
            className={`bg-red-500 hover:bg-red-600 text-white ${(!selectedTask || timerStatus === "idle") && "opacity-50"}`}
          >
            <Square size={16} className="mr-2" />
            Stop
          </Button>
        </div>
      </div>
    </div>
  );
};