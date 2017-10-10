/*
 * tracing_tools.hpp
 *
 *  Created on: 04.08.2015
 *      Author: ingo
 */

#ifndef CLIENTS_ROSCPP_INCLUDE_ROS_TRACING_TOOLS_H_
#define CLIENTS_ROSCPP_INCLUDE_ROS_TRACING_TOOLS_H_

#include "ros/callback_queue_interface.h"

namespace ros {
	class SubscriptionCallbackHelper;
	typedef boost::shared_ptr<SubscriptionCallbackHelper> SubscriptionCallbackHelperPtr;

	class TracingTools {
	public:
		static void trace_task_init(const char* task_name, const char* owner=NULL);
		static void trace_node_init(const char* node_name, unsigned int roscpp_version);

		static const void* getCallbackFunction(const CallbackInterfacePtr& cb);
		static std::string getCallbackInfo(const CallbackInterfacePtr& cb);
		/**
		 * Emit tracing information linking the function ptr's name to the
		 * given reference pointer.
		 */
		static void trace_name_info(const void* fun_ptr, const void* ref);

		static void trace_message_processed(const char* message_name,
				const void* callback_ref, const uint32_t receipt_time_sec,
				const uint32_t receipt_time_nsec);

		//static void trace_name_info(const boost::bind_t& bound_func, const void* ref);
		/** Emit tracing information that the callback has been called with
		 * the given data.
		 * */
		/*static void trace_cb_call(const void* ptr_ref, const void* data, const
				uint64_t trace_id);*/

		static void trace_call_start(const void* ptr_ref, const void* data,
				const uint64_t trace_id);
		static void trace_call_end(const void* ptr_ref, const void* data,
				const uint64_t trace_id);

		static void trace_queue_delay(const char* queue_name,
				const void* ptr_ref, const void* data,
				const uint32_t entry_time_sec, const uint32_t entry_time_nsec);


		/**
		 * Emit tracing information that the timer identified by
		 * 'timer_ref' has been scheduled for invocation on the callback-queue
		 * using the wrapper callback 'callback_ref'.
		 */
		static void trace_timer_scheduled(const void* callback_ref,
				const void* timer_ref);

		static void trace_new_connection(const char* local_hostport_arg,
											  const char* remote_hostport_arg,
											  const void* channel_ref_arg,
											  const char* channel_type_arg,
											  const char* name_arg,
											  const char* data_type_arg);
		static void trace_publisher_link_handle_message(const void* channel_ref_arg,
														const void* buffer_ref_arg);
		static void trace_publisher_message_queued(const char* topic_arg,
												   const void* buffer_ref_arg);
		static void trace_subscriber_link_message_write(const void* message_ref_arg,
														const void* channel_ref_arg);
		static void trace_subscriber_link_message_dropped(const void* message_ref_arg);
		static void trace_subscription_message_queued(const char* topic_arg,
													  const void* buffer_ref_arg,
													  const void* queue_ref_arg,
													  const void* callback_ref_arg,
													  const void* message_ref_arg,
													  int receipt_time_sec_arg,
													  int receipt_time_nsec_arg);
		static void trace_subscriber_callback_added(const void* queue_ref_arg,
													const void* callback_ref_arg,
													const char* type_info_arg,
													const char* data_type_arg,
													const char* source_name_arg,
													int queue_size_arg);
	};

	std::string get_backtrace(int index = -1);
	std::string get_symbol(void* funptr);


	/**
	 * Traces the function pointer, the name of the function it points
	 * to, and the helper that will be used to call it.
	 */
	void trace_callback_wrapper(void* func_ptr,
			const SubscriptionCallbackHelperPtr& helper);

	/** Emit a trace message for a link in a processing chain.
			 * @param element the containing link element (usually 'this')
			 * @param caller_name if available, a reference to the caller of this
			 * 	element
			 * @param in_data_ref a pointer to the incoming data element,
			 *   for association to the preceding link
			 * @param out_data_ref a pointer to the outgoing data element, for
			 *   association with the succeeding link
			 * @param trace_id an optional id for distinguishing different traces
			 *   where the data ref's are the same
			 * */
	void trace_link(const char* element_name,
			const void* caller_name,
			const void* in_data_ref,
			const void* out_data_ref,
			const uint64_t trace_id);
}


#endif /* CLIENTS_ROSCPP_INCLUDE_ROS_TRACING_TOOLS_H_ */
