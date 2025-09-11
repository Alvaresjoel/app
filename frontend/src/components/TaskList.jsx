import { Clock, User, FolderOpen } from "lucide-react";
import Badge from "./ui/Badge";
import Card from "./ui/Card";
import { TasksContext } from "../store/tasks-context";
import { useContext, useEffect } from "react";
import { UserContext } from "../store/user-context";

export default function TaskList() {
    const {tasks, isLoading, selectedTask, handleTaskSelect, fetchUserTask, timerStatus} = useContext(TasksContext);
    const {user} = useContext(UserContext);

    useEffect(()=>{
        if (user?.ace_user_id) {
            fetchUserTask(user.ace_user_id)
        }
        console.log("Timer status:", timerStatus);
    }, [user?.ace_user_id, timerStatus])

    return (
        <div className="space-y-3">
            {tasks?.map((task) => {
                const disabled =
                    task.status === "completed" ||
                    (timerStatus === "running" && selectedTask?.task_id !== task.task_id);

                return (
                    <Card
                        key={task.task_id}
                        className={`p-4 transition-all duration-200 ${
                            disabled
                                ? "opacity-50 cursor-not-allowed"
                                : "cursor-pointer hover:shadow-md hover:border-blue-200"
                        } ${
                            selectedTask?.task_id === task.task_id
                                ? "ring-2 ring-blue-500 border-blue-300 bg-blue-50"
                                : ""
                        }`}
                        onClick={() => !disabled && handleTaskSelect(task, user)}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-3 mb-2">
                                    <h3 className="font-medium truncate">{task.name}</h3>
                                    <Badge status={task.status}>{task.status}</Badge>
                                </div>

                                <div className="flex items-center gap-4 text-sm text-gray-500">
                                    <div className="flex items-center gap-1">
                                        <FolderOpen size={14} />
                                        <span>{task.project_name}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <User size={14} />
                                        <span>{task.supervisor_name}</span>
                                    </div>
                                </div>
                            </div>

                            {selectedTask?.task_id === task.task_id && (
                                <div className="flex items-center text-blue-600 ml-4">
                                    <Clock size={18} />
                                </div>
                            )}
                        </div>
                    </Card>
                );
            })}

            {isLoading && tasks?.length === 0 && (
                <Card className="p-8 text-center">
                    <div className="text-gray-400">
                        <Clock size={48} className="mx-auto mb-4 opacity-30 animate-spin" />
                        <p>Loading tasks...</p>
                    </div>
                </Card>
            )}

            {!isLoading && tasks?.length === 0 && (
                <Card className="p-8 text-center">
                    <div className="text-gray-400">
                        <p>No tasks available</p>
                    </div>
                </Card>
            )}
        </div>
    );
}