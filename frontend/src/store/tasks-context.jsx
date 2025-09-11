import { createContext, useEffect, useState } from 'react';
import { fetchTasks, getDuration, getLatestLog } from '../services/api';

export const TasksContext = createContext({
  tasks: [],
  isLoading: false,
  selectedTask: null,
  elapsedTime: 0,
  logId: null,
  timerStatus: "idle",
  handleTaskSelect: () => { },
  setElapsedTime: () => { },
  setLogId: () => { },
  fetchUserTask: () => { },
  setTimerStatus: () => { }
});

export function TasksContextProvider({ children }) {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [logId, setLogId] = useState(null);
  const [timerStatus, setTimerStatus] = useState("idle");

  useEffect(() => {
    async function fetchDuration() {
      if (!logId) {
        setElapsedTime(0);
        return;
      }

      try {
        const data = await getDuration(logId);
        // Assuming data has shape { log_id, duration }
        if (data && typeof data.duration === 'number') {
          setElapsedTime(data.duration);
        } else {
          setElapsedTime(0);
        }
      } catch (error) {
        console.error('Failed to fetch duration:', error);
        setElapsedTime(0);
      }
    }

    fetchDuration();
  }, [selectedTask, logId]);

  const handleTaskSelect = async (task, user) => {
  setSelectedTask(task);
  setTimerStatus("idle");
  setElapsedTime(0);
  setLogId(null);

  try {
    if (!task || !task.id || !user?.user_id) return;

    const data = await getLatestLog({
      user_id: user.user_id,
      task_id: task.id,
    });

    if (data?.log_id) {
      setLogId(data.log_id);
      setElapsedTime(data.duration || 0);
    } else {
      setElapsedTime(0);
    }
  } catch (error) {
    console.error("Failed to fetch latest log:", error);
    setElapsedTime(0);
  }
};


  async function fetchUserTask(ace_user_id) {
    setIsLoading(true)
    const data = await fetchTasks(ace_user_id)

    setTasks(Array.isArray(data) ? data.map((t) => ({
      id: t.task_id,
      task_id: t.task_id,
      name: t.task_name ?? t.name ?? t.task_title,
      project_name: t.project_name,
      supervisor_name: t.supervisor_name,
      status: t.status ?? "pending"
    })) : [])
    setIsLoading(false)
  }

  const contextValue = {
    tasks: tasks,
    isLoading,
    selectedTask,
    handleTaskSelect,
    elapsedTime,
    setElapsedTime,
    setLogId,
    logId,
    fetchUserTask,
    timerStatus,
    setTimerStatus
  };

  return <TasksContext.Provider value={contextValue}>{children}</TasksContext.Provider>;
}