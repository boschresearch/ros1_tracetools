// Copyright (c) 2016, 2017 - for information on the respective copyright owner
// see the NOTICE file and/or the repository https://github.com/bosch-ros-pkg/tracetools.git
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


#include <tracetools/tracetools.h>
#ifdef WITH_LTTNG
#include "tp_call.h"
#endif
#include <execinfo.h>
#include <sstream>
#include <sys/prctl.h>
#include "ros/callback_queue_interface.h"

namespace ros {
namespace trace {

bool compile_status() throw () {
#ifdef WITH_LTTNG
	return true;
#else
	return false;
#endif
}
void task_init(const char* name, const char* owner) {
#ifdef WITH_LTTNG
	std::ostringstream oss;
	oss << name << "_";
	if (owner != NULL && strlen(owner) > 0) {
		oss << owner;
	} else {
		char thread_name[256];
		prctl(PR_GET_NAME, thread_name, NULL, NULL, NULL);
		oss << thread_name;
	}
	std::string fqn(oss.str());
	tracepoint(roscpp, task_start, fqn.c_str());

	// check if we need to truncate, because name is usually not unique
	// and we need the procname to disambiguate
	if (strlen(name) > 10) {
		oss.str(fqn.substr(0, 8));
		// let prctl truncate the rest
		oss << "_" << fqn.substr(strlen(name));
		fqn = oss.str();
	}
	prctl(PR_SET_NAME, fqn.c_str(), NULL, NULL, NULL);
#endif
}
void node_init(const char* node_name, unsigned int roscpp_version) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, init_node, node_name, roscpp_version);
	prctl(PR_SET_NAME, node_name, NULL, NULL, NULL);
#endif
}
void call_start(const void* ptr_ref, const void* data,
		const uint64_t trace_id) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, callback_start, ptr_ref, data, trace_id);
#endif
}
void call_end(const void* ptr_ref, const void* data, const uint64_t trace_id) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, callback_end, ptr_ref, data, trace_id);
#endif
}

void message_processed(const char* message_name, const void* callback_ref,
		const uint32_t receipt_time_sec, const uint32_t receipt_time_nsec) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, message_processed, message_name, callback_ref,
			receipt_time_sec, receipt_time_nsec);
#endif
}


void fn_name_info(const void* const_ptr, const void* ptr) {
#ifdef WITH_LTTNG
	void* func_ptr = const_cast<void*>(const_ptr);
	char** symbols = backtrace_symbols(&func_ptr, 1);
	// check if we just got a pointer
	if (symbols[0][0] == '[') {
		tracepoint(roscpp, ptr_name_info, impl::get_backtrace().c_str(), ptr);
	} else {
		tracepoint(roscpp, ptr_name_info, symbols[0], ptr);
	}
	free(symbols);
#endif
}
/*void cb_call(const void* ptr_ref, const void* data, const
 uint64_t trace_id) {
 tracepoint(roscpp, ptr_call, ptr_ref, data, trace_id);
 }*/


void timer_added(const void* fun_ptr, const char* type_info, int period_sec,
		int period_nsec) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, timer_added, fun_ptr,
			impl::get_symbol(const_cast<void*>(fun_ptr)).c_str(), type_info,
			period_sec, period_nsec);
#endif
}

void timer_scheduled(const void* callback_ref, const void* timer_ref) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, timer_scheduled, callback_ref, timer_ref);
#endif
}

void time_sleep(const void* callback_ref, int sleep_sec, int sleep_nsec) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, time_sleep, callback_ref, sleep_sec, sleep_nsec);
#endif
}

void callback_wrapper(void* func_ptr,
		const SubscriptionCallbackHelperPtr& helper) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, ptr_name_info, impl::get_symbol(func_ptr).c_str(),
			helper.get());
#endif
}

void link_step(const char* element_name, const void* caller_ref,
		const void* in_data_ref, const void* out_data_ref,
		const uint64_t trace_id) {
#ifdef WITH_LTTNG
#ifdef NO_LINK_BACKTRACES
	tracepoint(roscpp, trace_link, element_name, user_name,
			in_data_ref, out_data_ref, trace_id, NULL);
#else
	tracepoint(roscpp, trace_link, element_name, typeid(caller_ref).name(),
			caller_ref, in_data_ref, out_data_ref, trace_id,
			impl::get_backtrace().c_str());
#endif
#endif
}

void new_connection(const char* local_hostport_arg,
		const char* remote_hostport_arg, const void* channel_ref_arg,
		const char* channel_type_arg, const char* name_arg,
		const char* data_type_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, new_connection, local_hostport_arg, remote_hostport_arg,
			channel_ref_arg, channel_type_arg, name_arg, data_type_arg);
#endif
}
void publisher_link_handle_message(const void* channel_ref_arg,
		const void* buffer_ref_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, publisher_link_handle_message, channel_ref_arg,
			buffer_ref_arg);
#endif
}

void publisher_message_queued(const char* topic_arg,
		const void* buffer_ref_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, publisher_message_queued, topic_arg, buffer_ref_arg);
#endif
}
void publisher_message_queued(const std::string& topic_arg,
		const void* buffer_ref_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, publisher_message_queued, topic_arg.c_str(),
			buffer_ref_arg);
#endif
}
void subscriber_link_message_write(const void* message_ref_arg,
		const void* channel_ref_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, subscriber_link_message_write, message_ref_arg,
			channel_ref_arg);
#endif
}
void subscriber_link_message_dropped(const void* message_ref_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, subscriber_link_message_dropped, message_ref_arg);
#endif
}

void subscription_message_queued(const char* topic_arg,
		const void* buffer_ref_arg, const void* queue_ref_arg,
		const void* callback_ref_arg, const void* message_ref_arg,
		int receipt_time_sec_arg, int receipt_time_nsec_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, subscription_message_queued, topic_arg, buffer_ref_arg,
			queue_ref_arg, callback_ref_arg, message_ref_arg,
			receipt_time_sec_arg, receipt_time_nsec_arg);
#endif
}
void subscription_message_dropped(const char* topic_arg, 
			const void* buffer_ref_arg,
			const void* queue_ref_arg,
			const void* callback_ref_arg,
			const void* message_ref_arg,
			int receipt_time_sec_arg,
			int receipt_time_nsec_arg)
{
#ifdef WITH_LTTNG
	tracepoint(roscpp, subscription_message_dropped, topic_arg, buffer_ref_arg,
			queue_ref_arg, callback_ref_arg, message_ref_arg,
			receipt_time_sec_arg, receipt_time_nsec_arg);
#endif
}
void subscriber_callback_added(const void* queue_ref_arg,
		const void* callback_ref_arg, const char* type_info_arg,
		const char* data_type_arg, const char* source_name_arg,
		int queue_size_arg) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, subscriber_callback_added, queue_ref_arg,
			callback_ref_arg, type_info_arg, data_type_arg, source_name_arg,
			queue_size_arg);
#endif
}

void subscriber_call_start(const std::string& topic, const void* queue_ref,
		const void* callback_ref, const void* message_ref, int receipt_time_sec,
		int receipt_time_nsec) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, subscriber_callback_start, topic.c_str(), 0, queue_ref,
			callback_ref, message_ref, receipt_time_sec, receipt_time_nsec);
#endif
}
void subscriber_call_end(const std::string& topic, const void* queue_ref,
		const void* callback_ref, const void* message_ref, int receipt_time_sec,
		int receipt_time_nsec) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, subscriber_callback_end, topic.c_str(), 0, queue_ref,
			callback_ref, message_ref, receipt_time_sec, receipt_time_nsec);
#endif
}

void queue_delay(const char* queue_name, const void* ptr_ref, const void* data,
		const uint32_t entry_time_sec, const uint32_t entry_time_nsec) {
#ifdef WITH_LTTNG
	tracepoint(roscpp, queue_delay, queue_name, ptr_ref, data, entry_time_sec,
			entry_time_nsec);
#endif
}

namespace impl {
std::string get_backtrace(int index) {
#ifdef WITH_LTTNG
	const int bufsize = 50;
	void* bt_buffer[bufsize];
	int size = backtrace(bt_buffer, bufsize);
	char** symbols = backtrace_symbols(bt_buffer, size);

	std::ostringstream oss;
	if (index < size) {
		if (index < 0) {
			// add full backtrace (excepting ourselves and our immediate
			// caller)
			for (int i = 2; i < size; ++i) {
				oss << symbols[i] << "|";
			}
		} else {
			oss << symbols[index];
		}
	} else
		oss << "Invalid index " << index << " requested, only have " << size
				<< " backtrace entries";

	free(symbols);

	return oss.str();
#else
	return "";
#endif
}

std::string get_symbol(void* funptr) {
#ifdef WITH_LTTNG
	char** symbols = backtrace_symbols(&funptr, 1);
	std::string result(symbols[0]);
	free(symbols);
	return result;
#else
	return "";
#endif
}
const void* getCallbackFunction(const CallbackInterfacePtr& cb) {
#ifdef WITH_LTTNG
	return cb.get();
#else
	return NULL;
#endif
}

std::string getCallbackInfo(const CallbackInterfacePtr& cb) {
#ifdef WITH_LTTNG
	void* funptr = const_cast<void*>(getCallbackFunction(cb));
	char** symbols = backtrace_symbols(&funptr, 1);
	std::string result(symbols[0]);
	free(symbols);
	return typeid(*cb).name() + std::string(" ") + result;
#else
	return "";
#endif
}
}


}
}
