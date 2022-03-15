#pragma once


#include <cstdint>

#include "platform_api.h"
#include "cpputils/typed_linked_list.hpp"
#include "cpputils/typed_list.hpp"
#include "cpputils/typed_dict.hpp"
#include "cpputils/flags_helper.hpp"
#include "logging/logger.hpp"
#include "profiling/profiling.hpp"





namespace profiling 
{

struct Metrics
{
    uint32_t ops = 0;
    uint32_t macs = 0;
    
    void operator = (const Metrics &other )
    {
        ops = other.ops;
        macs = other.macs;
    }

    void operator += (const Metrics &other )
    {
        ops += other.ops;
        macs += other.macs;
    }
};


struct Stats
{
    uint32_t time_us = 0;
    uint32_t cpu_cycles = 0;
    uint32_t accelerator_cycles = 0;

    void reset()
    {
        time_us = 0;
        cpu_cycles = 0;
        accelerator_cycles = 0;
    }

    void operator = (const Stats &other )
    {
        time_us = other.time_us;
        cpu_cycles = other.cpu_cycles;
        accelerator_cycles = other.accelerator_cycles;
    }


    void operator += (const Stats &other )
    {
        time_us += other.time_us;
        cpu_cycles += other.cpu_cycles;
        accelerator_cycles = other.accelerator_cycles;
    }
};

struct StatsAccumulator
{
    volatile uint32_t start_base = 0;
    volatile uint32_t start_marker = 0;
    uint32_t accumulator = 0;

    void reset()
    {
        start_base = 0;
        start_marker = 0;
        accumulator = 0;
    }
};

enum class Flag  : uint16_t
{
    None = 0,
    ReportTotalChildrenCycles               = (1 << 0),
    ExcludeFromTotalChildrenCyclesReport    = (1 << 1),
    ReportsFreeRunningCpuCycles             = (1 << 2),
    ExcludeStatsFromReport                  = (1 << 3),
    TimeMeasuredBetweenStartAndStop         = (1 << 4),
};
DEFINE_ENUM_CLASS_BITMASK_OPERATORS(Flag, uint16_t)

typedef cpputils::FlagsHelper<Flag> Flags;

typedef void (CustomStatsPrinter)(Profiler& profiler, logging::Logger& logger, const char* level_str);


class Profiler : public cpputils::LinkedListItem
{
public:
    cpputils::TypedDict<int32_t> custom_stats;

    const char* name() const;
    const char* fullname(Fullname& fullname) const;
    virtual void reset(void);
    constexpr const Stats& stats() const { return _stats; };
    constexpr Stats& stats() { return _stats; };
    constexpr const Metrics& metrics() const { return _metrics; };
    constexpr Metrics& metrics() { return _metrics; };
    Metrics metrics_including_children() const;
    void metrics(const Metrics& metrics);

    void flags(Flags flags);
    constexpr const Flags& flags() const { return _flags; };
    constexpr Flags& flags() { return _flags; };

    void msg(const char* msg);
    const char* msg() const;

    bool parent(Profiler *parent);
    constexpr Profiler* parent() const { return _parent; };
    constexpr const cpputils::TypedList<Profiler*>& children() const { return _children; } 

    void custom_stats_printer(CustomStatsPrinter* printer);
    int32_t increment_custom_stat(const char* name, int32_t amount=1);
    int32_t get_custom_stat(const char* name) const;

   
    void inline start(void)
    {
        if(_state != State::Started)
        {
            const uint32_t current_cycle = platform_get_cpu_cycle();
            const uint32_t current_time_us = platform_get_timestamp_us();
            if(_state == State::Stopped)
            {
                _cpu_accumulator.start_base = current_cycle;
                _time_accumulator.start_base = current_time_us;
            }
            _state = State::Started;
            _cpu_accumulator.start_marker = current_cycle;
            _time_accumulator.start_marker = current_time_us;
        }
    }

    void inline stop(void)
    {
        const volatile uint32_t stop_cpu_cycle = platform_get_cpu_cycle();
        const volatile uint32_t stop_time_us = platform_get_timestamp_us();
        update_stats(true, stop_cpu_cycle, stop_time_us);
    }

    void inline pause(void)
    {
        const volatile uint32_t stop_cpu_cycle = platform_get_cpu_cycle();
        const volatile uint32_t stop_time_us = platform_get_timestamp_us();
        update_stats(false, stop_cpu_cycle, stop_time_us);
    }


// protected:
    enum class State : uint8_t
    {
        Stopped,
        Started,
        Paused
    } _state = State::Stopped;

    
    Metrics _metrics;
    Stats _stats;
    cpputils::TypedList<Profiler*> _children;

    StatsAccumulator _cpu_accumulator;
    StatsAccumulator _time_accumulator;
    Flags _flags;
    const char* _msg = nullptr;
    cpputils::LinkedListItem *_linked_list_next = nullptr;
    Profiler *_parent = nullptr;
    CustomStatsPrinter* _custom_stats_printer = nullptr;
    const char* _name = nullptr;
    bool _was_visited = false;
    void* _object_buffer = nullptr;



    Profiler(void* object_buffer, const char* name);
 
    static uint32_t required_alloc_size(const char* name)
    {
        return sizeof(Profiler) + strlen(name) + 1;
    }

    virtual void update_stats(bool stop, uint32_t stop_cpu_cycle, uint32_t stop_time_us);
    void get_child_metrics(const Profiler *profiler, Metrics &metrics) const;
    void next(cpputils::LinkedListItem* next) override;
    cpputils::LinkedListItem* next() override;
    void unlink() override;

    MAKE_CLASS_NON_ASSIGNABLE(Profiler);
};




class AveragedProfiler : public Profiler
{
public:
    void reset(void) override;
    void update_stats(bool stop, uint32_t stop_cpu_cycle, uint32_t stop_time_us) override;


    uint64_t total_time_us = 0;
    uint64_t total_cpu_cycles = 0;
    uint32_t total_count = 0;

    AveragedProfiler(void* object_buffer, const char* name) : Profiler(object_buffer, name){}

    static uint32_t required_alloc_size(const char* name)
    {
        return sizeof(AveragedProfiler) + strlen(name) + 1;
    }
};

} // namespace profiling

